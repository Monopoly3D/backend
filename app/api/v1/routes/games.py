from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.controllers.games import GamesController
from app.assets.game import Game

games_router: APIRouter = APIRouter(prefix="/games", tags=["Games"])


@games_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Game
)
async def create_game(
        games_controller: Annotated[GamesController, Depends(GamesController.dependency)]
) -> Game:
    game: Game = await games_controller.create_game()

    return game


@games_router.get(
    "/{uuid}",
    status_code=status.HTTP_200_OK,
    response_model=Game
)
async def get_game(
        uuid: UUID,
        games_controller: Annotated[GamesController, Depends(GamesController.dependency)]
) -> Game:
    game: Game = await games_controller.get_game(uuid)

    return game


@games_router.delete(
    "/{uuid}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_game(
        uuid: UUID,
        games_controller: Annotated[GamesController, Depends(GamesController.dependency)]
) -> None:
    await games_controller.remove_game(uuid)
