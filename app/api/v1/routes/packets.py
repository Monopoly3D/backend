import asyncio
from inspect import getfullargspec
from typing import Dict, Any, Callable, Type, Coroutine

from fastapi import APIRouter
from jwt import decode, InvalidTokenError
from starlette.websockets import WebSocket

from app.api.v1.exceptions.invalid_packet_error import InvalidPacketError
from app.api.v1.packets.base import BasePacket
from app.api.v1.packets.client.auth import ClientAuthPacket
from app.api.v1.packets.server.auth_response import ServerAuthResponsePacket
from app.api.v1.packets.server.error import ServerErrorPacket
from app.api.v1.routes.abstract_packets import AbstractPacketsRouter
from config import Config


class PacketsRouter(APIRouter, AbstractPacketsRouter):
    config: Config = Config(_env_file=".env")

    def __init__(
            self,
            *,
            prefix: str
    ) -> None:
        super().__init__(prefix=prefix)
        self.handlers: Dict[Type[BasePacket], Coroutine[Any, Any, BasePacket]] = {}

        self.add_api_websocket_route("/", self.handle_packets)

    async def handle_packets(
            self,
            websocket: WebSocket
    ) -> None:
        await websocket.accept()

        try:
            auth_packet: ClientAuthPacket = ClientAuthPacket.unpack(await websocket.receive_text())
        except InvalidPacketError:
            await websocket.close(3000, "Provided authorization packet data is invalid")
            return
        try:
            ticket: Dict[str, Any] = await self.__decode_auth_ticket(auth_packet.ticket)
        except InvalidTokenError:
            await websocket.close(3000, "Provided authorization ticket is invalid")
            return
        if "user_id" not in ticket or "username" not in ticket:
            await websocket.close(3000, "Provided authorization ticket is invalid")
            return

        auth_response_packet: ServerAuthResponsePacket = ServerAuthResponsePacket(
            ticket["user_id"],
            ticket["username"]
        )
        await websocket.send_text(auth_response_packet.pack())

        while True:  # TODO: Fix
            packet: str = await websocket.receive_text()

            try:
                packet_type: Type[BasePacket] = BasePacket.withdraw_packet_type(packet)
            except InvalidPacketError:
                await websocket.send_text(ServerErrorPacket(4000, "Provided packet meta is invalid").pack())
                continue
            try:
                packet: BasePacket = packet_type.unpack(packet)
            except InvalidPacketError:
                await websocket.send_text(ServerErrorPacket(4000, "Provided packet data is invalid").pack())
                continue

            handler: Any = self.handlers.get(packet_type, None)
            if handler is None:
                await websocket.send_text(ServerErrorPacket(4001, "Provided packet type was not handled").pack())
                continue

            prepared_args: Dict[str, Any] = self.__prepare_args(handler, packet=packet, websocket=websocket)
            response_packet: BasePacket = await handler(**prepared_args)

            await websocket.send_text(response_packet.pack())

    def handle(
            self,
            packet: Type[BasePacket]
    ) -> Callable:
        def decorator(func: Coroutine[Any, Any, BasePacket]) -> None:
            self.handlers.update({packet: func})

        return decorator

    async def __decode_auth_ticket(
            self,
            ticket: str
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(
            decode,
            ticket,
            self.config.jwt_key.get_secret_value(),
            algorithms=[self.config.jwt_algorithm]
        )

    @staticmethod
    def __prepare_args(
            func: Coroutine[Any, Any, BasePacket],
            **kwargs: Any
    ) -> Dict[str, Any]:
        return {
            k: arg for k, arg in kwargs.items()
            if k in getfullargspec(func)[0]
        }
