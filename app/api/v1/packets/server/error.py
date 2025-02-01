from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet_error import InvalidPacketError
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.packets.base import BasePacket


class ServerErrorPacket(BasePacket):
    PACKET_TAG = "server_error"
    PACKET_CLASS = PacketClass.SERVER

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

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        if "status_code" not in packet or "detail" not in packet:
            raise InvalidPacketError("Provided packet data is invalid")

        return cls(packet["status_code"], packet["detail"])

    def to_json(self) -> Dict[str, Any]:
        return {
            "status_code": self.status_code,
            "detail": self.detail
        }
