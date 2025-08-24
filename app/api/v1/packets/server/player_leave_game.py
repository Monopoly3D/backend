from typing import Dict, Any, List, TYPE_CHECKING

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket

if TYPE_CHECKING:
    from app.assets.objects.player import Player
else:
    Player = Any


@dataclass
class ServerPlayerLeaveGamePacket(ServerPacket):
    PACKET_TAG = "player_leave_game"

    players: List[Player]

    def to_json(self) -> Dict[str, Any]:
        return {
            "players": [player.to_json() for player in self.players]
        }
