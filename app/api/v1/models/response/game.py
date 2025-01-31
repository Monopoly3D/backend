from uuid import UUID

from pydantic import BaseModel

from app.assets.redis.game import Game


class GameResponseModel(BaseModel):
    id: UUID
    is_started: bool

    @classmethod
    def from_game(
            cls,
            game: Game
    ) -> 'GameResponseModel':
        return cls(
            id=game.game_id,
            is_started=game.is_started
        )
