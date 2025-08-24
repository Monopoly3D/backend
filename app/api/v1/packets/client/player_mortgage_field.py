from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerMortgageFieldPacket(ClientPacket):
    PACKET_TAG = "player_mortgage_field"

    field: int

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(
            packet["field"]
        )
