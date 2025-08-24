from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerAcceptAuctionPacket(ServerPacket):
    PACKET_TAG = "player_accept_auction"

    player_id: UUID
    cost: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "cost": self.cost
        }
