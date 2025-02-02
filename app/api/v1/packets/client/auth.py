from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.packets.base_client import ClientPacket


class ClientAuthPacket(ClientPacket):
    PACKET_TAG = "auth"
    PACKET_CLASS = PacketClass.CLIENT

    PACKET_KEYS = ["ticket"]

    def __init__(
            self,
            ticket: str
    ) -> None:
        self.ticket = ticket

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(packet["ticket"])
