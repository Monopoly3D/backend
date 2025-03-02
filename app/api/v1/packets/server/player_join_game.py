from typing import Dict, Any, List
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.player import Player


class ServerPlayerJoinGamePacket(ServerPacket):
    PACKET_TAG = "player_join_game"

    def __init__(
            self,
            game_id: UUID,
            players: List[Player]
    ) -> None:
        self.game_id = game_id
        self.players = players

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "players": [player.to_json() for player in self.players]
        }
