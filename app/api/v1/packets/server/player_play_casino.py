from typing import Dict, Any, List
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerPlayerPlayCasinoPacket(ServerPacket):
    PACKET_TAG = "player_play_casino"

    game_id: UUID
    player_id: UUID
    balance: int
    dices: List[int]
    roll: int
    won: bool
    prize: int

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "dices": self.dices,
            "roll": self.roll,
            "won": self.won,
            "prize": self.prize
        }
