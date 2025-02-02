from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.controllers.games import GamesController
from app.api.v1.exceptions.http.not_found_error import NotFoundError
from app.api.v1.models.response.game import GameResponseModel
from app.api.v1.security.authenticator import Authenticator
from app.assets.objects.game import Game

games_router: APIRouter = APIRouter(prefix="/games", tags=["Games"])


@games_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=GameResponseModel,
    dependencies=[Authenticator.verify_access_token_dependency()]
)
async def create_game(
        games_controller: Annotated[GamesController, Depends(GamesController.dependency)]
) -> GameResponseModel:
    game: Game = await games_controller.create_game()
    return GameResponseModel.from_game(game)


@games_router.get(
    "/{game_id}",
    status_code=status.HTTP_200_OK,
    response_model=GameResponseModel,
    dependencies=[Authenticator.verify_access_token_dependency()]
)
async def get_game(
        game_id: UUID,
        games_controller: Annotated[GamesController, Depends(GamesController.dependency)]
) -> GameResponseModel:
    game: Game | None = await games_controller.get_game(game_id)

    if game is None:
        raise NotFoundError("Game with provided UUID was not found")

    return GameResponseModel.from_game(game)


@games_router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Authenticator.verify_access_token_dependency()]
)
async def remove_game(
        game_id: UUID,
        games_controller: Annotated[GamesController, Depends(GamesController.dependency)]
) -> None:
    if not await games_controller.exists_game(game_id):
        raise NotFoundError("Game with provided UUID was not found")

    await games_controller.remove_game(game_id)
