from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerEnterGamePacket(ClientPacket):
    PACKET_TAG = "player_enter_game"

    ticket: str

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(packet["ticket"])
