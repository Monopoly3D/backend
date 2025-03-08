from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPingPacket(ServerPacket):
    PACKET_TAG = "ping"

    def to_json(self) -> Dict[str, Any]:
        return {"status": "ok"}
