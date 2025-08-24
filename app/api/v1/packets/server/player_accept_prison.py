from typing import Dict, Any, Tuple
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerAcceptPrisonPacket(ServerPacket):
    PACKET_TAG = "player_accept_prison"

    player_id: UUID
    dices: Tuple[int, ...]
    got_double: bool

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "dices": list(self.dices),
            "got_double": self.got_double
        }
