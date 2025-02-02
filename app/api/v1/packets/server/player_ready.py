from typing import Dict, Any
from uuid import UUID

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet_error import InvalidPacketError
from app.api.v1.packets.base import BasePacket


class ServerPlayerReadyPacket(BasePacket):
    PACKET_TAG = "server_player_ready"
    PACKET_CLASS = PacketClass.SERVER

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
        if "game_id" not in packet or "player_id" not in packet:
            raise InvalidPacketError("Provided packet data is invalid")

        try:
            game_id = UUID(packet["game_id"])
            player_id = UUID(packet["player_id"])
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")

        if "is_ready" not in packet:
            raise InvalidPacketError("Provided packet data is invalid")

        return cls(game_id, player_id, packet["is_ready"])

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "is_ready": self.is_ready
        }
