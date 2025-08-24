from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerPayRentPacket(ServerPacket):
    PACKET_TAG = "player_pay_rent"

    player_id: UUID
    owner_id: UUID
    field: int
    player_balance: int
    owner_balance: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "owner_id": str(self.owner_id),
            "field": self.field,
            "player_balance": self.player_balance,
            "owner_balance": self.owner_balance
        }
