from typing import Dict, Any

from app.api.v1.packets.base_client import ClientPacket


class ClientPingPacket(ClientPacket):
    PACKET_TAG = "ping"

    def __init__(self) -> None:
        pass

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        return cls()
