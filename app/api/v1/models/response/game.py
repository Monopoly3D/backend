from typing import List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, model_serializer

from app.api.v1.models.response.field import FieldResponseModel
from app.api.v1.models.response.player import PlayerResponseModel
from app.assets.objects.game import Game


class GameResponseModel(BaseModel):
    game_id: UUID
    code: str
    is_started: bool
    round: int
    move: int
    player_amount: int
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
            code=game.code,
            is_started=game.is_started,
            round=game.round,
            move=game.move,
            player_amount=game.player_amount,
            players=game.players.models_list,
            fields=game.fields.models_list,
            with_players=with_players,
            with_fields=with_fields
        )

    @model_serializer()
    def serialize_model(self) -> Dict[str, Any]:
        model: Dict[str, Any] = {
            "game_id": self.game_id,
            "code": self.code,
            "is_started": self.is_started,
            "round": self.round,
            "move": self.move,
            "player_amount": self.player_amount
        }

        if self.with_players:
            model["players"] = self.players
        if self.with_fields:
            model["fields"] = self.fields

        return model
