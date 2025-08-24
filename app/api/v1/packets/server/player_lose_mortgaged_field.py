from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerLoseMortgagedFieldPacket(ServerPacket):
    PACKET_TAG = "player_lose_mortgaged_field"

    field: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "field": self.field
        }
