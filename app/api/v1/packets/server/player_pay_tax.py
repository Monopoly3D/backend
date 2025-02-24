from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerPlayerPayTaxPacket(ServerPacket):
    PACKET_TAG = "player_pay_tax"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            balance: int
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.balance = balance

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "balance": self.balance
        }
