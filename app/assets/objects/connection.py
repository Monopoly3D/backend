import asyncio
from asyncio import CancelledError
from typing import Any, TYPE_CHECKING, Annotated

from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.packets.base_server import ServerPacket

if TYPE_CHECKING:
    from app.assets.objects.connections import Connections


class Connection(WebSocket):
    __CONNECTION_REMOVAL_DELAY: float = 0.5

    def __init__(
            self,
            *args: Any,
            connections: Connections,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.connections = connections

    async def send_packet(
            self,
            packet: ServerPacket
    ) -> None:
        try:
            await self.send_text(packet.pack())
        except (WebSocketDisconnect, RuntimeError, CancelledError):
            await asyncio.sleep(self.__CONNECTION_REMOVAL_DELAY)
            await self.connections.remove_connection(
                await self.connections.get_user_id(self)
            )

    @staticmethod
    def dependency(
            websocket: WebSocket,
            connections: Annotated[Connections, Connections.dependency]
    ) -> 'Connection':
        return Connection(
            websocket,
            connections=connections
        )
