from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerMustPayTaxPacket(ServerPacket):
    PACKET_TAG = "player_must_pay_tax"

    game_id: UUID
    player_id: UUID
    amount: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "amount": self.amount
        }
