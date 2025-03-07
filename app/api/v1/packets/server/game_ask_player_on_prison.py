from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerGameAskPlayerOnPrisonPacket(ServerPacket):
    PACKET_TAG = "game_ask_player_on_prison"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            cost: int
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.cost = cost

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "cost": self.cost
        }
