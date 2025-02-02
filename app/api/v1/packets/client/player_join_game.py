from typing import Dict, Any
from uuid import UUID

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base import BasePacket


class ClientPlayerJoinGamePacket(BasePacket):
    PACKET_TAG = "client_player_join_game"
    PACKET_CLASS = PacketClass.CLIENT

    PACKET_KEYS = ["game_id"]

    def __init__(
            self,
            game_id: UUID
    ) -> None:
        self.game_id = game_id

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        try:
            return cls(UUID(packet["game_id"]))
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")

    def to_json(self) -> Dict[str, Any]:
        return {"game_id": str(self.game_id)}
