from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerJoinGamePacket(ClientPacket):
    PACKET_TAG = "player_join_game"

    ticket: str

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(packet["ticket"])
