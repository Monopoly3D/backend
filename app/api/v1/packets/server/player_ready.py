from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerReadyPacket(ServerPacket):
    PACKET_TAG = "player_ready"

    player_id: UUID
    is_ready: bool

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "is_ready": self.is_ready
        }
