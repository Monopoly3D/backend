from typing import Dict, Any
from uuid import UUID

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base import BasePacket


class ServerAuthPacket(BasePacket):
    PACKET_TAG = "server_auth"
    PACKET_CLASS = PacketClass.SERVER

    def __init__(
            self,
            user_id: UUID,
            username: str
    ) -> None:
        self.user_id = user_id
        self.username = username

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        if "user_id" not in packet:
            raise InvalidPacketError("Provided packet data is invalid")

        try:
            user_id = UUID(packet["user_id"])
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")

        if "username" not in packet:
            raise InvalidPacketError("Provided packet data is invalid")

        return cls(user_id, packet["username"])

    def to_json(self) -> Dict[str, Any]:
        return {
            "user_id": str(self.user_id),
            "username": self.username
        }
