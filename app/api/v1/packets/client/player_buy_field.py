from typing import Dict, Any
from uuid import UUID

from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base_client import ClientPacket


class ClientPlayerBuyFieldPacket(ClientPacket):
    PACKET_TAG = "player_buy_field"

    PACKET_KEYS = ["game_id", "field"]

    def __init__(
            self,
            game_id: UUID,
            field: int
    ) -> None:
        self.game_id = game_id
        self.field = field

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        try:
            return cls(
                UUID(packet["game_id"]),
                packet["field"]
            )
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")
