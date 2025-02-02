from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.packets.base_client import ClientPacket


class ClientPingPacket(ClientPacket):
    PACKET_TAG = "ping"
    PACKET_CLASS = PacketClass.CLIENT

    PACKET_KEYS = ["request"]

    def __init__(
            self,
            request: str
    ) -> None:
        self.request = request

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(packet["request"])
