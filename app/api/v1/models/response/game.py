from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.api.v1.models.response.field import FieldResponseModel
from app.api.v1.models.response.player import PlayerResponseModel
from app.assets.objects.game import Game


class GameResponseModel(BaseModel):
    id: UUID
    is_started: bool
    current_round: int
    current_move: int
    has_start_bonus: bool
    min_players: int
    max_players: int
    start_delay: int
    players: List[PlayerResponseModel]
    fields: List[FieldResponseModel]

    @classmethod
    def from_game(
            cls,
            game: Game
    ) -> 'GameResponseModel':
        return cls(
            id=game.game_id,
            is_started=game.is_started,
            current_round=game.round,
            current_move=game.move,
            has_start_bonus=game.has_start_bonus,
            min_players=game.min_players,
            max_players=game.max_players,
            start_delay=game.start_delay,
            players=[PlayerResponseModel.from_player(player) for player in game.players],
            fields=[FieldResponseModel.from_field(field) for field in game.fields]
        )
