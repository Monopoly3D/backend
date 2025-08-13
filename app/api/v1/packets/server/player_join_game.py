from typing import Dict, Any, List
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.player import Player


@dataclass
class ServerPlayerJoinGamePacket(ServerPacket):
    PACKET_TAG = "player_join_game"

    game_id: UUID
    players: List[Player]

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "players": [
                {
                    "player_id": str(player.player_id),
                    "username": player.username,
                    "is_ready": player.is_ready
                }
                for player in self.players
            ]
        }
