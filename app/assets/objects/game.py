from typing import Dict, Any, List
from uuid import UUID

from app.api.v1.controllers.redis import RedisController
from app.assets.objects.fields.field import Field
from app.assets.objects.player import Player
from app.assets.objects.redis import RedisObject


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
        self.fields = fields

        if fields is None:
            self.fields = self.default_fields()

        super().__init__(controller.REDIS_KEY.format(game_id=game_id), controller)

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "is_started": self.is_started,
            "round": self.round,
            "move": self.move,
            "has_start_bonus": self.has_start_bonus,
            "players": self.players_json,
            "fields": self.fields_json
        }

    @property
    def players_json(self) -> List[Dict[str, Any]]:
        return [player.to_json() for player in self.players]

    @property
    def fields_json(self) -> List[Dict[str, Any]]:
        return [field.to_json() for field in self.fields]

    def default_fields(self) -> List[Field]:
        return []
