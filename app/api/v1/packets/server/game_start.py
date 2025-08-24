from typing import Dict, Any, List

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.fields.abstract import AbstractField
from app.assets.objects.player import Player


@dataclass
class ServerGameStartPacket(ServerPacket):
    PACKET_TAG = "game_start"

    players: List[Player]
    fields: List[AbstractField]

    def to_json(self) -> Dict[str, Any]:
        return {
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
