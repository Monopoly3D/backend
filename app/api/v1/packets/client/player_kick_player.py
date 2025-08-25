from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerKickPlayerPacket(ClientPacket):
    PACKET_TAG = "player_kick_player"

    player_id: UUID

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(
            UUID(packet["player_id"])
        )
