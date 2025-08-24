from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerSellFiliationPacket(ClientPacket):
    PACKET_TAG = "player_sell_filiation"

    field: int

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(
            packet["field"]
        )
