from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerGameCountdownStartPacket(ServerPacket):
    PACKET_TAG = "game_countdown_start"

    delay: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "delay": self.delay
        }
