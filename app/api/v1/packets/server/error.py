from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerErrorPacket(ServerPacket):
    PACKET_TAG = "error"

    status_code: int
    detail: str

    @classmethod
    def from_error(
            cls,
            error: WebSocketError
    ) -> 'ServerErrorPacket':
        return cls(error.status_code, str(error))

    def to_json(self) -> Dict[str, Any]:
        return {
            "status_code": self.status_code,
            "detail": self.detail
        }
