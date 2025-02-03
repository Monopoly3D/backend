from inspect import getfullargspec
from typing import Dict, Any, Callable, Type, Coroutine, Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.controllers.users import UsersController
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.exceptions.websocket.internal_server_error import InternalServerError
from app.api.v1.exceptions.websocket.invalid_packet_data import InvalidPacketDataError
from app.api.v1.exceptions.websocket.unknown_packet import UnknownPacketError
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.logging import logger
from app.api.v1.packets.base_client import ClientPacket
from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.server.ping import ServerPingPacket
from app.api.v1.routes.websocket.abstract_packets import AbstractPacketsRouter
from app.api.v1.security.authenticator import Authenticator
from app.assets.objects.user import User
from app.dependencies import Dependency
from config import Config


async def dependencies(
        config: Annotated[Config, Depends(Dependency.config_websocket)],
        redis: Annotated[Redis, Depends(Dependency.redis_websocket)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.websocket_dependency)],
        connections: Annotated[ConnectionsController, Depends(ConnectionsController.websocket_dependency)],
        users_controller: Annotated[UsersController, Depends(UsersController.websocket_dependency)],
        games_controller: Annotated[GamesController, Depends(GamesController.websocket_dependency)],
        user: Annotated[User, Authenticator.get_websocket_user()]
) -> Dict[str, Any]:
    return {
        "config": config,
        "redis": redis,
        "authenticator": authenticator,
        "connections": connections,
        "users_controller": users_controller,
        "games_controller": games_controller,
        "user": user
    }


class PacketsRouter(APIRouter, AbstractPacketsRouter):
    def __init__(
            self,
            *,
            prefix: str
    ) -> None:
        super().__init__(prefix=prefix)

        self.add_api_websocket_route(
            "/",
            self.handle_packets,
            dependencies=[Authenticator.authenticate_websocket_dependency()]
        )

        self.handlers: Dict[Type[ClientPacket], Coroutine[Any, Any, ServerPacket | None]] = {}

        @self.handle(ClientPingPacket)
        async def on_client_ping() -> ServerPingPacket:
            return ServerPingPacket()

    def handle(
            self,
            packet: Type[ClientPacket]
    ) -> Callable:
        def decorator(func: Coroutine[Any, Any, ServerPacket]) -> None:
            self.handlers.update({packet: func})

        return decorator

    async def handle_packets(
            self,
            websocket: WebSocket,
            dp: Annotated[Dict[str, Any], Depends(dependencies)]
    ) -> None:
        try:
            while True:
                try:
                    await self.__handle_packet(
                        websocket,
                        **dp
                    )
                except WebSocketError as e:
                    raise e
                except Exception as e:
                    raise InternalServerError("Internal server error", e)
        except WebSocketDisconnect as e:
            logger.info(f"Closing connection. Status code: {e.code}, Reason: {e.reason}")

    async def __handle_packet(
            self,
            websocket: WebSocket,
            **kwargs
    ) -> None:
        packet: str = await websocket.receive_text()

        try:
            packet_type: Type[ClientPacket] = ClientPacket.withdraw_packet_type(packet)
            packet: ClientPacket = packet_type.unpack(packet)
        except InvalidPacketError:
            raise InvalidPacketDataError("Provided packet data is invalid")

        handler: Any = self.handlers.get(packet_type, None)
        if handler is None:
            raise UnknownPacketError("Unknown packet type")

        prepared_args: Dict[str, Any] = self.__prepare_args(
            handler,
            packet=packet,
            websocket=websocket,
            **kwargs
        )
        response_packet: ServerPacket | None = await handler(**prepared_args)

        if response_packet is not None:
            await websocket.send_text(response_packet.pack())

    @staticmethod
    def __prepare_args(
            func: Coroutine[Any, Any, ServerPacket | None],
            **kwargs: Any
    ) -> Dict[str, Any]:
        return {
            k: arg for k, arg in kwargs.items()
            if k in getfullargspec(func)[0]
        }
