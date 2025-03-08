from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket
from app.assets.enums.monopoly_type import MonopolyType


@dataclass
class ServerPlayerGainMonopolyPacket(ServerPacket):
    PACKET_TAG = "player_gain_monopoly"

    game_id: UUID
    player_id: UUID
    monopoly_type: MonopolyType

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "monopoly_type": self.monopoly_type.value
        }
