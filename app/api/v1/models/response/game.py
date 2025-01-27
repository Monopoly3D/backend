from uuid import UUID

from app.api.v1.models.response.base import BaseResponseModel
from app.assets.game import Game


class GameResponseModel(BaseResponseModel):
    uuid: UUID
    is_started: bool

    @classmethod
    def from_game(cls, game: Game) -> 'GameResponseModel':
        return cls(
            uuid=game.uuid,
            is_started=game.is_started
        )
