from typing import List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, model_serializer

from app.api.v1.models.response.action import ActionResponseModel
from app.api.v1.models.response.field import FieldResponseModel
from app.api.v1.models.response.player import PlayerResponseModel
from app.assets.objects.game import Game


class GameResponseModel(BaseModel):
    game_id: UUID
    host_id: UUID
    code: str
    is_started: bool
    round: int
    move: int
    player_amount: int
    action: ActionResponseModel | None
    start_delay: int
    start_bonus: int
    start_reward: int
    start_bonus_round_amount: int
    auction_minimum_bet: int
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
            with_fields: bool = True
    ) -> 'GameResponseModel':
        return cls(
            game_id=game.game_id,
            host_id=game.host_id,
            code=game.code,
            is_started=game.is_started,
            round=game.round,
            move=game.move,
            player_amount=game.player_amount,
            action=ActionResponseModel.from_action(game.action),
            start_delay=game.start_delay,
            start_bonus=game.start_bonus,
            start_reward=game.start_reward,
            start_bonus_round_amount=game.start_bonus_round_amount,
            auction_minimum_bet=game.auction_minimum_bet,
            players=game.players.models_list,
            fields=game.fields.models_list,
            with_players=with_players,
            with_fields=with_fields
        )

    @model_serializer()
    def serialize_model(self) -> Dict[str, Any]:
        model: Dict[str, Any] = {
            "game_id": self.game_id,
            "host_id": self.host_id,
            "code": self.code,
            "is_started": self.is_started,
            "round": self.round,
            "move": self.move,
            "player_amount": self.player_amount,
            "action": self.action,
            "start_delay": self.start_delay,
            "start_bonus": self.start_bonus,
            "start_reward": self.start_reward,
            "start_bonus_round_amount": self.start_bonus_round_amount,
            "auction_minimum_bet": self.auction_minimum_bet
        }

        if self.with_players:
            model["players"] = self.players
        if self.with_fields:
            model["fields"] = self.fields

        return model
