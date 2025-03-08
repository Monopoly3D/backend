from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerGameCountdownStartPacket(ServerPacket):
    PACKET_TAG = "game_countdown_start"

    game_id: UUID
    delay: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "delay": self.delay
        }
