from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base import BasePacket


class ClientAuthPacket(BasePacket):
    PACKET_TAG = "client_auth"
    PACKET_CLASS = PacketClass.CLIENT

    PACKET_KEYS = ["ticket"]

    def __init__(
            self,
            ticket: str
    ) -> None:
        self.ticket = ticket

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        return cls(packet["ticket"])

    def to_json(self) -> Dict[str, Any]:
        return {"ticket": self.ticket}
