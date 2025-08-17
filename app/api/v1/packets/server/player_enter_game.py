from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.game_code import GameCode


@dataclass
class ServerPlayerEnterGamePacket(ServerPacket):
    PACKET_TAG = "player_enter_game"

    game_id: UUID
    code: GameCode
    min_players: int
    max_players: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "code": self.code,
            "min_players": self.min_players,
            "max_players": self.max_players
        }
