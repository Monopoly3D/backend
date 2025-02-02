from typing import Dict, Any
from uuid import UUID

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base_client import ClientPacket


class ClientPlayerReadyPacket(ClientPacket):
    PACKET_TAG = "player_ready"
    PACKET_CLASS = PacketClass.CLIENT

    PACKET_KEYS = ["game_id", "is_ready"]

    def __init__(
            self,
            game_id: UUID,
            is_ready: bool
    ) -> None:
        self.game_id = game_id
        self.is_ready = is_ready

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        try:
            return cls(
                UUID(packet["game_id"]),
                packet["is_ready"]
            )
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")
