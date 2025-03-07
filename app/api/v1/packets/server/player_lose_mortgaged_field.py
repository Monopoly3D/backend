from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerPlayerLoseMortgagedFieldPacket(ServerPacket):
    PACKET_TAG = "player_lose_mortgaged_field"

    def __init__(
            self,
            game_id: UUID,
            field: int
    ) -> None:
        self.game_id = game_id
        self.field = field

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "field": self.field
        }
