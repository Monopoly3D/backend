from typing import Dict, Any, TYPE_CHECKING

from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket

if TYPE_CHECKING:
    from app.assets.objects.game import Game
else:
    Game = Any


@dataclass
class ServerPlayerEnterGamePacket(ServerPacket):
    PACKET_TAG = "player_enter_game"

    game: Game

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": self.game.game_id,
            "host_id": self.game.host_id,
            "code": self.game.code,
            "is_started": self.game.is_started,
            "round": self.game.round,
            "move": self.game.move,
            "player_amount": self.game.player_amount,
            "action": self.game.action.to_json(),
            "start_delay": self.game.start_delay,
            "start_bonus": self.game.start_bonus,
            "start_reward": self.game.start_reward,
            "start_bonus_round_amount": self.game.start_bonus_round_amount,
            "auction_minimum_bet": self.game.auction_minimum_bet,
            "players": self.game.players.to_json(),
            "fields": self.game.fields.to_json()
        }
