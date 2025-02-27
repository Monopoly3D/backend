from typing import Dict, Any
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerPlayerPayRentPacket(ServerPacket):
    PACKET_TAG = "player_pay_rent"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            owner_id: UUID,
            field: int,
            player_balance: int,
            owner_balance: int
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.owner_id = owner_id
        self.field = field
        self.player_balance = player_balance
        self.owner_balance = owner_balance

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "owner_id": str(self.owner_id),
            "field": self.field,
            "player_balance": self.player_balance,
            "owner_balance": self.owner_balance
        }
