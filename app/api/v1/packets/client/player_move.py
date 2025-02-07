from typing import Dict, Any
from uuid import UUID

from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base_client import ClientPacket


class ClientPlayerMovePacket(ClientPacket):
    PACKET_TAG = "player_move"

    PACKET_KEYS = ["game_id"]

    def __init__(
            self,
            game_id: UUID
    ) -> None:
        self.game_id = game_id

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        try:
            return cls(UUID(packet["game_id"]))
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")
