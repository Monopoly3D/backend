from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerGameMovePacket(ServerPacket):
    PACKET_TAG = "game_move"

    def __init__(
            self,
            game_id: UUID,
            current_round: int,
            current_move: int
    ) -> None:
        self.game_id = game_id
        self.round = current_round
        self.move = current_move

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "round": self.round,
            "move": self.move
        }
