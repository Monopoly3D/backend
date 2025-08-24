from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerGameAskPlayerOnAuctionPacket(ServerPacket):
    PACKET_TAG = "game_ask_player_on_auction"

    player_id: UUID
    field: int
    cost: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "field": self.field,
            "cost": self.cost
        }
