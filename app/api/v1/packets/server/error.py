from typing import Dict, Any

from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.packets.base_server import ServerPacket


class ServerErrorPacket(ServerPacket):
    PACKET_TAG = "error"

    PACKET_KEYS = ["status_code", "detail"]

    def __init__(
            self,
            status_code: int,
            detail: str
    ) -> None:
        self.status_code = status_code
        self.detail = detail

    @classmethod
    def from_error(
            cls,
            error: WebSocketError
    ) -> 'ServerErrorPacket':
        return cls(
            status_code=error.status_code,
            detail=str(error)
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "status_code": self.status_code,
            "detail": self.detail
        }
