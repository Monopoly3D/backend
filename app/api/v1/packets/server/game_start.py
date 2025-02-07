from typing import Dict, Any, List
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.field import Field
from app.assets.objects.player import Player


class ServerGameStartPacket(ServerPacket):
    PACKET_TAG = "game_start"

    def __init__(
            self,
            game_id: UUID,
            players: List[Player],
            fields: List[Field]
    ) -> None:
        self.game_id = game_id
        self.players = players
        self.fields = fields

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "players": [
                {
                    "player_id": str(player.player_id),
                    "balance": player.balance,
                    "field": player.field
                }
                for player in self.players
            ],
            "fields": [field.to_json() for field in self.fields]
        }
