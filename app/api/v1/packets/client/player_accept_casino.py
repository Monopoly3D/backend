from typing import Dict, Any, List
from uuid import UUID

from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base_client import ClientPacket


class ClientPlayerAcceptCasinoPacket(ClientPacket):
    PACKET_TAG = "player_accept_casino"

    PACKET_KEYS = ["game_id", "dices"]

    def __init__(
            self,
            game_id: UUID,
            dices: List[int]
    ) -> None:
        self.game_id = game_id
        self.dices = dices

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'ClientPacket':
        try:
            return cls(UUID(packet["game_id"]), packet["dices"])
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")
