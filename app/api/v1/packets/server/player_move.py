from typing import Dict, Any, Tuple
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerPlayerMovePacket(ServerPacket):
    PACKET_TAG = "player_move"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            dices: Tuple[int, int],
            field: int
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.dices = dices
        self.field = field

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "dices": list(self.dices),
            "field": self.field
        }
