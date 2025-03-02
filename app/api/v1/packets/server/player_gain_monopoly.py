from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket
from app.assets.enums.monopoly_type import MonopolyType


class ServerPlayerGainMonopolyPacket(ServerPacket):
    PACKET_TAG = "player_gain_monopoly"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            monopoly_type: MonopolyType
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.monopoly_type = monopoly_type

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "monopoly_type": self.monopoly_type.value
        }
