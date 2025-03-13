from typing import Dict, Any, Tuple
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerMovePacket(ServerPacket):
    PACKET_TAG = "player_move"

    game_id: UUID
    player_id: UUID
    dices: Tuple[int, ...]
    field: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "dices": list(self.dices),
            "field": self.field
        }
