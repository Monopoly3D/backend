from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerGameCountdownStopPacket(ServerPacket):
    PACKET_TAG = "game_countdown_stop"

    PACKET_KEYS = ["game_id"]

    def __init__(
            self,
            game_id: UUID
    ) -> None:
        self.game_id = game_id

    def to_json(self) -> Dict[str, Any]:
        return {"game_id": str(self.game_id)}
