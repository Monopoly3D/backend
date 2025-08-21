from pydantic import BaseModel

from app.assets.parameters import Parameters


class CreateGameModel(BaseModel):
    player_amount: int = Parameters.DEFAULT_PLAYER_AMOUNT
