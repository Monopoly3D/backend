from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerLoseMortgagedFieldPacket(ServerPacket):
    PACKET_TAG = "player_lose_mortgaged_field"

    game_id: UUID
    field: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "field": self.field
        }
