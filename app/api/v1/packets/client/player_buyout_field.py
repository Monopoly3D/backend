from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerBuyoutFieldPacket(ClientPacket):
    PACKET_TAG = "player_buyout_field"

    game_id: UUID
    field: int

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(UUID(packet["game_id"]), packet["field"])
