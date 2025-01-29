from typing import Dict, Any

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.invalid_packet_error import InvalidPacketError
from app.api.v1.packets.base_packet import BasePacket


class ServerPingPacket(BasePacket):
    PACKET_TAG = "server_ping"
    PACKET_CLASS = PacketClass.SERVER

    def __init__(
            self,
            response: str
    ) -> None:
        self.response = response

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        if "response" not in packet:
            raise InvalidPacketError("Provided packet data is invalid")

        return cls(packet["response"])

    def to_json(self) -> Dict[str, Any]:
        return {"response": self.response}
