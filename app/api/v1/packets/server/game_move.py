from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerGameMovePacket(ServerPacket):
    PACKET_TAG = "game_move"

    player_id: UUID
    current_round: int
    current_move: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "round": self.current_round,
            "move": self.current_move
        }
