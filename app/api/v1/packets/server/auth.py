from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerAuthPacket(ServerPacket):
    PACKET_TAG = "auth"

    PACKET_KEYS = ["user_id", "username"]

    def __init__(
            self,
            user_id: UUID,
            username: str
    ) -> None:
        self.user_id = user_id
        self.username = username

    def to_json(self) -> Dict[str, Any]:
        return {
            "user_id": str(self.user_id),
            "username": self.username
        }
