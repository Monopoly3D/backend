from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerPlayerReadyPacket(ServerPacket):
    PACKET_TAG = "player_ready"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            is_ready: bool
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.is_ready = is_ready

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "is_ready": self.is_ready
        }
