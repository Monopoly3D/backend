from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerReadyPacket(ClientPacket):
    PACKET_TAG = "player_ready"

    is_ready: bool

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(
            packet["is_ready"]
        )
