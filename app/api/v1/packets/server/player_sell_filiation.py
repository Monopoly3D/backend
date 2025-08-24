from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerSellFiliationPacket(ServerPacket):
    PACKET_TAG = "player_sell_filiation"

    player_id: UUID
    field: int
    filiation: int
    balance: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "field": self.field,
            "filiation": self.filiation,
            "balance": self.balance
        }
