from typing import Dict, Any, List
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerPlayerPlayCasinoPacket(ServerPacket):
    PACKET_TAG = "player_play_casino"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            balance: int,
            dices: List[int],
            roll: int,
            won: bool,
            prize: int
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.balance = balance
        self.dices = dices
        self.roll = roll
        self.won = won
        self.prize = prize

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "dices": self.dices,
            "roll": self.roll,
            "won": self.won,
            "prize": self.prize
        }
