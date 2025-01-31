from typing import Dict, Any, List
from uuid import UUID

from app.api.v1.controllers.redis import RedisController
from app.assets.field import Field
from app.assets.player import Player
from app.assets.redis import RedisObject


class Game(RedisObject):
    def __init__(
            self,
            game_id: UUID,
            *,
            is_started: bool = False,
            current_round: int = 0,
            current_move: int = 0,
            has_start_bonus: bool = True,
            players: List[Player] | None = None,
            fields: List[Field] | None = None,
            controller: RedisController
    ) -> None:
        self.game_id = game_id
        self.is_started = is_started
        self.round = current_round
        self.move = current_move
        self.has_start_bonus = has_start_bonus

        self.players = players or []
        self.fields = fields or []

        super().__init__(controller.REDIS_KEY.format(game_id=game_id), controller)

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "is_started": self.is_started
        }
