from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerAcceptPrisonPacket(ClientPacket):
    PACKET_TAG = "player_accept_prison"

    game_id: UUID

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(UUID(packet["game_id"]))
