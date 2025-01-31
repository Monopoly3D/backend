import asyncio
from inspect import getfullargspec
from typing import Dict, Any, Callable, Type, Coroutine, Annotated

from fastapi import APIRouter, Depends
from jwt import decode, InvalidTokenError
from redis.asyncio import Redis
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.exceptions.invalid_packet_error import InvalidPacketError
from app.api.v1.logging import logger
from app.api.v1.packets.base import BasePacket
from app.api.v1.packets.client.auth import ClientAuthPacket
from app.api.v1.packets.server.auth_response import ServerAuthResponsePacket
from app.api.v1.packets.server.error import ServerErrorPacket
from app.api.v1.routes.abstract_packets import AbstractPacketsRouter
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
            redis: Annotated[Redis, Depends(Dependency.redis_websocket)]
    ) -> None:
        await websocket.accept()
        authenticated: bool = await self.__authenticate_client(
            websocket,
            config.jwt_key.get_secret_value(),
            config.jwt_algorithm
        )

        if authenticated:
            try:
                while True:
                    try:
                        await self.__handle_packet(websocket, config=config, redis=redis)
                    except Exception as e:
                        try:
                            await websocket.send_text(ServerErrorPacket(4100, "Internal server error").pack())
                        except WebSocketDisconnect:
                            pass
                        logger.error(e)
            except WebSocketDisconnect as e:
                logger.info(f"Closing connection. Status code: {e.code}, Reason: {e.reason}")

    async def __handle_packet(
            self,
            websocket: WebSocket,
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

        prepared_args: Dict[str, Any] = self.__prepare_args(handler, packet=packet, websocket=websocket, **kwargs)
        response_packet: BasePacket = await handler(**prepared_args)

        await websocket.send_text(response_packet.pack())

    @staticmethod
    async def __authenticate_client(
            websocket: WebSocket,
            jwt_key: str,
            jwt_algorithm: str
    ) -> bool:
        try:
            auth_packet: ClientAuthPacket = ClientAuthPacket.unpack(await websocket.receive_text())
        except InvalidPacketError:
            await websocket.close(3000, "Provided authorization packet data is invalid")
            return False

        try:
            ticket: Dict[str, Any] = await asyncio.to_thread(
                decode,
                auth_packet.ticket,
                jwt_key,
                algorithms=[jwt_algorithm]
            )

            if "user_id" not in ticket or "username" not in ticket:
                raise InvalidTokenError
        except InvalidTokenError:
            await websocket.close(3000, "Provided authorization ticket is invalid")
            return False

        auth_response_packet: ServerAuthResponsePacket = ServerAuthResponsePacket(
            ticket["user_id"],
            ticket["username"]
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
