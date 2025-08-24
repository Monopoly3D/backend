from asyncio import CancelledError
from typing import Any

from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.packets.base_server import ServerPacket


class Connection(WebSocket):
    def __init__(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

    async def send_packet(
            self,
            packet: ServerPacket
    ) -> None:
        try:
            await self.send_text(packet.pack())
        except (WebSocketDisconnect, RuntimeError, CancelledError):
            pass

    @staticmethod
    def dependency(websocket: WebSocket) -> 'Connection':
        return Connection(websocket)
