from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from jwt import encode
from starlette import status

from app.api.v1.controllers.games import GamesController
from app.api.v1.models.response.game import GameResponseModel
from app.assets.game import Game
from app.dependencies import Dependency
from config import Config

games_router: APIRouter = APIRouter(prefix="/games", tags=["Games"])


@games_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=GameResponseModel
)
async def create_game(
        games_controller: Annotated[GamesController, GamesController.dependency()]
) -> GameResponseModel:
    game: Game = await games_controller.create_game()
    return GameResponseModel.from_game(game)


@games_router.get(
    "/{uuid}",
    status_code=status.HTTP_200_OK,
    response_model=GameResponseModel
)
async def get_game(
        uuid: UUID,
        games_controller: Annotated[GamesController, GamesController.dependency()]
) -> GameResponseModel:
    game: Game = await games_controller.get_game(uuid)
    return GameResponseModel.from_game(game)


@games_router.delete(
    "/{uuid}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_game(
        uuid: UUID,
        games_controller: Annotated[GamesController, GamesController.dependency()]
) -> None:
    await games_controller.remove_game(uuid)


@games_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=str
)
async def register(
        username: str,
        config: Annotated[Config, Depends(Dependency.config)]
) -> str:
    return encode(
        {
            "user_id": str(uuid4()),
            "username": username
        },
        key=config.jwt_key.get_secret_value(),
        algorithm=config.jwt_algorithm
    )
