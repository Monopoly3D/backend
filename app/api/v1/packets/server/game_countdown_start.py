from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerGameCountdownStartPacket(ServerPacket):
    PACKET_TAG = "game_countdown_start"

    def __init__(
            self,
            game_id: UUID,
            delay: int
    ) -> None:
        self.game_id = game_id
        self.delay = delay

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "delay": self.delay
        }
