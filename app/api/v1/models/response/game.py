from typing import List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, model_serializer

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

    with_players: bool
    with_fields: bool

    @classmethod
    def from_game(
            cls,
            game: Game,
            *,
            with_players: bool = True,
            with_fields: bool = False
    ) -> 'GameResponseModel':
        return cls(
            game_id=game.game_id,
            is_started=game.is_started,
            round=game.round,
            move=game.move,
            min_players=game.min_players,
            max_players=game.max_players,
            players=game.players.models_list,
            fields=game.fields.models_list,
            with_players=with_players,
            with_fields=with_fields
        )

    @model_serializer()
    def serialize_model(self) -> Dict[str, Any]:
        model: Dict[str, Any] = {
            "game_id": self.game_id,
            "is_started": self.is_started,
            "round": self.round,
            "move": self.move,
            "min_players": self.min_players,
            "max_players": self.max_players
        }

        if self.with_players:
            model["players"] = self.players
        if self.with_fields:
            model["fields"] = self.fields

        return model
