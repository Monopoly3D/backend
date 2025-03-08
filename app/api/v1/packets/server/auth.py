from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerAuthPacket(ServerPacket):
    PACKET_TAG = "auth"

    user_id: UUID
    username: str

    def to_json(self) -> Dict[str, Any]:
        return {
            "user_id": str(self.user_id),
            "username": self.username
        }
