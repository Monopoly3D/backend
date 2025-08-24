from typing import Dict, Any, List

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_client import ClientPacket


@dataclass
class ClientPlayerAcceptCasinoPacket(ClientPacket):
    PACKET_TAG = "player_accept_casino"

    dices: List[int]

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls(packet["dices"])
