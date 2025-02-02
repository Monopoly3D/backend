from typing import Dict, Any
from uuid import UUID

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base import BasePacket


class ServerPlayerReadyPacket(BasePacket):
    PACKET_TAG = "server_player_ready"
    PACKET_CLASS = PacketClass.SERVER

    PACKET_KEYS = ["game_id", "player_id", "is_ready"]

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            is_ready: bool
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.is_ready = is_ready

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        try:
            return cls(UUID(packet["game_id"]), UUID(packet["player_id"]), packet["is_ready"])
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "is_ready": self.is_ready
        }
