from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerMortgageFieldPacket(ClientPacket):
    PACKET_TAG = "player_mortgage_field"

    game_id: UUID
    field: int

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(UUID(packet["game_id"]), packet["field"])
