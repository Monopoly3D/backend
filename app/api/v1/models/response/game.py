from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.api.v1.models.response.field import FieldResponseModel
from app.api.v1.models.response.player import PlayerResponseModel
from app.assets.objects.game import Game


class GameResponseModel(BaseModel):
    game_id: UUID
    is_started: bool
    round: int
    move: int
    min_players: int
    max_players: int
    players: List[PlayerResponseModel]
    fields: List[FieldResponseModel]

    @classmethod
    def from_game(
            cls,
            game: Game
    ) -> 'GameResponseModel':
        return cls(
            game_id=game.game_id,
            is_started=game.is_started,
            round=game.round,
            move=game.move,
            min_players=game.min_players,
            max_players=game.max_players,
            players=[PlayerResponseModel.from_player(player) for player in game.players_list],
            fields=[FieldResponseModel.from_field(field) for field in game.fields]
        )
