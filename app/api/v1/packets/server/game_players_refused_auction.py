from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket


@dataclass
class ServerGamePlayersRefusedAuctionPacket(ServerPacket):
    PACKET_TAG = "game_players_refused_auction"

    def to_json(self) -> Dict[str, Any]:
        return {}
