from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerMustPayPrisonPacket(ServerPacket):
    PACKET_TAG = "player_must_pay_prison"

    player_id: UUID
    amount: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "amount": self.amount
        }
