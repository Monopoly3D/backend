from typing import Dict, Any, List
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerAcceptCasinoPacket(ClientPacket):
    PACKET_TAG = "player_accept_casino"

    game_id: UUID
    dices: List[int]

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(UUID(packet["game_id"]), packet["dices"])
