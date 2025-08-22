from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket
from app.assets.objects.code import GameCode


@dataclass
class ServerPlayerEnterGamePacket(ServerPacket):
    PACKET_TAG = "player_enter_game"

    game_id: UUID
    host_id: UUID
    code: GameCode
    player_amount: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "host_id": str(self.host_id),
            "code": self.code.to_json(),
            "player_amount": self.player_amount
        }
