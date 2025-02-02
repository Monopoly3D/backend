from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.player import Player


class ServerPlayerJoinGamePacket(ServerPacket):
    PACKET_TAG = "player_join_game"

    PACKET_KEYS = {
        "game_id": None,
        "player": [
            "id",
            "username",
            "balance",
            "field",
            "is_ready",
            "is_playing",
            "is_imprisoned",
            "double_amount",
            "contract_amount"
        ]
    }

    def __init__(
            self,
            game_id: UUID,
            player: Player
    ) -> None:
        self.game_id = game_id
        self.player = player

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player": {
                "id": str(self.player.player_id),
                "username": self.player.username,
                "balance": self.player.balance,
                "field": self.player.field,
                "is_ready": self.player.is_ready,
                "is_playing": self.player.is_playing,
                "is_imprisoned": self.player.is_imprisoned,
                "double_amount": self.player.double_amount,
                "contract_amount": self.player.contract_amount
            }
        }
