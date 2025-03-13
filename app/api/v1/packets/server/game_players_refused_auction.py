from typing import Dict, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerGamePlayersRefusedAuctionPacket(ServerPacket):
    PACKET_TAG = "game_players_refused_auction"

    game_id: UUID

    def to_json(self) -> Dict[str, Any]:
        return {"game_id": str(self.game_id)}
