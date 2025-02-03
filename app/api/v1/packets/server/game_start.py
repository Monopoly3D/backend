from typing import Dict, Any, List
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.player import Player


class ServerGameStartPacket(ServerPacket):
    PACKET_TAG = "game_start"

    PACKET_KEYS = ["game_id", "players"]

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
            "players": [str(player.player_id) for player in self.players]
        }
