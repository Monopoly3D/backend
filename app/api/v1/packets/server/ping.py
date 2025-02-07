from typing import Dict, Any

from app.api.v1.packets.base_server import ServerPacket


class ServerPingPacket(ServerPacket):
    PACKET_TAG = "ping"

    def __init__(self) -> None:
        pass

    def to_json(self) -> Dict[str, Any]:
        return {"status": "ok"}
