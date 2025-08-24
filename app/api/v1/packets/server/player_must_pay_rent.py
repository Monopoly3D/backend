from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerMustPayRentPacket(ServerPacket):
    PACKET_TAG = "player_must_pay_rent"

    player_id: UUID
    field: int
    amount: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "field": self.field,
            "amount": self.amount
        }
