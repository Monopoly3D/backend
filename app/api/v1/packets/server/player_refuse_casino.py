from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerRefuseCasinoPacket(ServerPacket):
    PACKET_TAG = "player_refuse_casino"

    player_id: UUID

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id)
        }
