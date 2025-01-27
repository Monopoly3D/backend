from uuid import UUID

from app.api.v1.models.response.base import BaseResponseModel
from app.assets.game import Game


class GameResponseModel(BaseResponseModel):
    uuid: UUID

    @classmethod
    def from_game(cls, game: Game) -> 'GameResponseModel':
        return cls(uuid=game.uuid)
