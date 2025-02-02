from typing import Dict, Any

from app.api.v1.packets.base_server import ServerPacket


class ServerPingPacket(ServerPacket):
    PACKET_TAG = "ping"

    PACKET_KEYS = ["response"]

    def __init__(
            self,
            response: str
    ) -> None:
        self.response = response

    def to_json(self) -> Dict[str, Any]:
        return {"response": self.response}
