from uuid import UUID

from pydantic import BaseModel

from app.assets.game import Game


class GameResponseModel(BaseModel):
    id: UUID
    is_started: bool

    @classmethod
    def from_game(
            cls,
            game: Game
    ) -> 'GameResponseModel':
        return cls(
            id=game.uuid,
            is_started=game.is_started
        )
