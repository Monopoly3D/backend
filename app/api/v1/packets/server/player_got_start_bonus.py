from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerGotStartBonusPacket(ServerPacket):
    PACKET_TAG = "player_got_start_bonus"

    player_id: UUID
    balance: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "balance": self.balance
        }
