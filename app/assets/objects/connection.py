from asyncio import CancelledError

from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.packets.base_server import ServerPacket


class Connection:
    def __init__(
            self,
            websocket: WebSocket
    ) -> None:
        self.websocket = websocket

    async def send(
            self,
            packet: ServerPacket
    ) -> None:
        await self.send_text(packet.pack())

    async def send_text(
            self,
            text: str
    ) -> None:
        try:
            await self.websocket.send_text(text)
        except (WebSocketDisconnect, RuntimeError, CancelledError):
            pass

    @staticmethod
    def dependency(websocket: WebSocket) -> 'Connection':
        return Connection(websocket)
