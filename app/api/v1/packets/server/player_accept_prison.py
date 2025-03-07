from typing import Dict, Any, Tuple
from uuid import UUID

from app.api.v1.packets.base_server import ServerPacket


class ServerPlayerAcceptPrisonPacket(ServerPacket):
    PACKET_TAG = "player_accept_prison"

    def __init__(
            self,
            game_id: UUID,
            player_id: UUID,
            dices: Tuple[int, ...],
            got_double: int
    ) -> None:
        self.game_id = game_id
        self.player_id = player_id
        self.dices = dices
        self.got_double = got_double

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "dices": list(self.dices),
            "got_double": self.got_double
        }
