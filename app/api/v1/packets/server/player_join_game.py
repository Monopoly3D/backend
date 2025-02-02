from typing import Dict, Any
from uuid import UUID

from app.api.v1.enums.packet_class import PacketClass
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.packets.base import BasePacket
from app.assets.objects.player import Player


class ServerPlayerJoinGamePacket(BasePacket):
    PACKET_TAG = "server_player_join_game"
    PACKET_CLASS = PacketClass.SERVER

    PACKET_KEYS = {
        "game_id": None,
        "player": [
            "id",
            "username",
            "balance",
            "field",
            "is_ready",
            "is_playing",
            "is_imprisoned",
            "double_amount",
            "contract_amount"
        ]
    }

    def __init__(
            self,
            game_id: UUID,
            player: Player
    ) -> None:
        self.game_id = game_id
        self.player = player

    @classmethod
    def from_json(cls, packet: Dict[str, Any]) -> 'BasePacket':
        try:
            return cls(UUID(packet["game_id"]), Player.from_json(packet["player"]))
        except ValueError:
            raise InvalidPacketError("Provided packet data is invalid")

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player": {
                "id": str(self.player.player_id),
                "username": self.player.username,
                "balance": self.player.balance,
                "field": self.player.field,
                "is_ready": self.player.is_ready,
                "is_playing": self.player.is_playing,
                "is_imprisoned": self.player.is_imprisoned,
                "double_amount": self.player.double_amount,
                "contract_amount": self.player.contract_amount
            }
        }
