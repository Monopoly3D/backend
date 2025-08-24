import asyncio
import logging
from asyncio import CancelledError
from typing import Any, Annotated

from starlette.datastructures import QueryParams, Headers, Address
from starlette.types import Message
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.connections import Connections


class Connection:
    __CONNECTION_REMOVAL_DELAY: float = 0.5

    def __init__(
            self,
            websocket: WebSocket,
            connections: Connections
    ) -> None:
        self.websocket = websocket
        self.connections = connections

    async def send_packet(
            self,
            packet: ServerPacket
    ) -> None:
        try:
            await self.send_text(packet.pack())
        except Exception as e:
            logging.getLogger().exception(e)
            await self.remove()

    async def remove(self) -> None:
        await self.close()
        await asyncio.sleep(self.__CONNECTION_REMOVAL_DELAY)
        await self.connections.remove_connection(await self.connections.get_user_id(self))

    async def receive(self) -> Message:
        return await self.websocket.receive()

    async def send(self, message: Message) -> None:
        await self.websocket.send(message)

    async def accept(self) -> None:
        await self.websocket.accept()

    async def receive_text(self) -> str:
        return await self.websocket.receive_text()

    async def receive_json(self, mode: str = "text") -> Any:
        return await self.websocket.receive_json(mode)

    async def send_text(self, data: str) -> None:
        await self.websocket.send_text(data)

    async def send_json(self, data: Any, mode: str = "text") -> None:
        await self.websocket.send_json(data, mode)

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        await self.websocket.close(code, reason)

    @property
    def app(self) -> Any:
        return self.websocket.app

    @property
    def headers(self) -> Headers:
        return self.websocket.headers

    @property
    def query_params(self) -> QueryParams:
        return self.websocket.query_params

    @property
    def client(self) -> Address | None:
        return self.websocket.client

    @staticmethod
    def dependency(
            websocket: WebSocket,
            connections: Annotated[Connections, Connections.dependency]
    ) -> 'Connection':
        return Connection(websocket, connections)
