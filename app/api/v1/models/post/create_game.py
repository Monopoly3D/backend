from typing import Annotated

from pydantic import BaseModel, Field

from app.assets.parameters import Parameters


class CreateGameModel(BaseModel):
    player_amount: Annotated[
        int,
        Field(ge=Parameters.MIN_PLAYERS, le=Parameters.MAX_PLAYERS)
    ] = Parameters.DEFAULT_PLAYER_AMOUNT
