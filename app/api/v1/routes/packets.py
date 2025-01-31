import asyncio
from inspect import getfullargspec
from typing import Dict, Any, Callable, Type, Coroutine, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.controllers.games import GamesController
from app.api.v1.controllers.users import UsersController
from app.api.v1.exceptions.invalid_access_token_error import InvalidAccessTokenError
from app.api.v1.exceptions.invalid_packet_error import InvalidPacketError
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.api.v1.logging import logger
from app.api.v1.packets.base import BasePacket
from app.api.v1.packets.client.auth import ClientAuthPacket
from app.api.v1.packets.connection_manager import ConnectionManager
from app.api.v1.packets.server.auth_response import ServerAuthResponsePacket
from app.api.v1.packets.server.error import ServerErrorPacket
from app.api.v1.routes.abstract_packets import AbstractPacketsRouter
from app.api.v1.security.authenticator import Authenticator
from app.assets.objects.user import User
from app.dependencies import Dependency
from config import Config


class PacketsRouter(APIRouter, AbstractPacketsRouter):
    def __init__(
            self,
            *,
            prefix: str
    ) -> None:
        super().__init__(prefix=prefix)
        self.add_api_websocket_route("/", self.handle_packets)

        self.handlers: Dict[Type[BasePacket], Coroutine[Any, Any, BasePacket]] = {}

    def handle(
            self,
            packet: Type[BasePacket]
    ) -> Callable:
        def decorator(func: Coroutine[Any, Any, BasePacket]) -> None:
            self.handlers.update({packet: func})

        return decorator

    async def handle_packets(
            self,
            websocket: WebSocket,
            config: Annotated[Config, Depends(Dependency.config_websocket)],
            redis: Annotated[Redis, Depends(Dependency.redis_websocket)],
            connection_manager: Annotated[ConnectionManager, Depends(ConnectionManager.websocket_dependency)],
            authenticator: Annotated[Authenticator, Depends(Authenticator.websocket_dependency)],
            users_controller: Annotated[UsersController, Depends(UsersController.websocket_dependency)],
            games_controller: Annotated[GamesController, Depends(GamesController.websocket_dependency)]
    ) -> None:
        await websocket.accept()

        try:
            authenticated: bool = await self.__authenticate_client(
                websocket,
                connection_manager,
                authenticator,
                users_controller
            )
        except WebSocketDisconnect:
            return

        if authenticated:
            try:
                while True:
                    try:
                        await self.__handle_packet(
                            websocket,
                            connection_manager,
                            config=config,
                            redis=redis,
                            authenticator=authenticator,
                            users_controller=users_controller,
                            games_controller=games_controller
                        )
                    except Exception as e:
                        try:
                            await websocket.send_text(ServerErrorPacket(4100, "Internal server error").pack())
                        except RuntimeError:
                            break
                        logger.error(e)
            except WebSocketDisconnect as e:
                logger.info(f"Closing connection. Status code: {e.code}, Reason: {e.reason}")

    async def __handle_packet(
            self,
            websocket: WebSocket,
            connection_manager: ConnectionManager,
            *,
            users_controller: UsersController,
            **kwargs
    ) -> None:
        packet: str = await websocket.receive_text()

        try:
            packet_type: Type[BasePacket] = BasePacket.withdraw_packet_type(packet)
            packet: BasePacket = packet_type.unpack(packet)
        except InvalidPacketError:
            await websocket.send_text(ServerErrorPacket(4000, "Provided packet data is invalid").pack())
            return

        handler: Any = self.handlers.get(packet_type, None)
        if handler is None:
            await websocket.send_text(ServerErrorPacket(4001, "Provided packet type was not handled").pack())
            return

        user: User = await users_controller.get_user(await connection_manager.get_user_id(websocket.client))

        if user is None:
            await websocket.send_text(
                ServerErrorPacket(4002, "Provided websocket address does not seem to be authenticated").pack()
            )
            return

        prepared_args: Dict[str, Any] = self.__prepare_args(
            handler,
            packet=packet,
            user=user,
            websocket=websocket,
            connection_manager=connection_manager,
            **kwargs
        )
        response_packet: BasePacket = await handler(**prepared_args)

        await websocket.send_text(response_packet.pack())

    @staticmethod
    async def __authenticate_client(
            websocket: WebSocket,
            connection_manager: ConnectionManager,
            authenticator: Authenticator,
            users_controller: UsersController
    ) -> bool:
        try:
            auth_packet: ClientAuthPacket = ClientAuthPacket.unpack(await websocket.receive_text())
        except InvalidPacketError:
            await websocket.close(3000, "Provided authorization packet data is invalid")
            return False

        try:
            ticket: Dict[str, str] = await asyncio.to_thread(
                authenticator.decode_ticket,
                auth_packet.ticket
            )
        except InvalidAccessTokenError:
            await websocket.close(3000, "Provided authorization ticket is invalid")
            return False

        try:
            user: User = await users_controller.get_user(UUID(ticket["id"]))
        except NotFoundError or ValueError:
            await websocket.close(3000, "Provided authorization ticket is invalid")
            return False

        await connection_manager.add_connection(websocket.client, user.user_id)

        auth_response_packet: ServerAuthResponsePacket = ServerAuthResponsePacket(
            user.user_id,
            user.username
        )

        await websocket.send_text(auth_response_packet.pack())
        return True

    @staticmethod
    def __prepare_args(
            func: Coroutine[Any, Any, BasePacket],
            **kwargs: Any
    ) -> Dict[str, Any]:
        return {
            k: arg for k, arg in kwargs.items()
            if k in getfullargspec(func)[0]
        }
