from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base import BasePacket


class ClientPingPacket(BasePacket):
    PACKET_TAG = "client_ping"
    PACKET_CLASS = PacketClass.CLIENT

    PACKET_KEYS = ["request"]

    def __init__(
            self,
            request: str
    ) -> None:
        self.request = request

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        return cls(packet["request"])

    def to_json(self) -> Dict[str, Any]:
        return {"request": self.request}
