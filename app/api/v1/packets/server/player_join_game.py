from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerPlayerJoinGamePacket(ServerPacket):
    PACKET_TAG = "player_join_game"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            username: str
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.username = username

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player": {
                "id": str(self.player_id),
                "username": self.username
            }
        }
