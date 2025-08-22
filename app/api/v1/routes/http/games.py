from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.api.v1.enums.permission import Permission
from app.api.v1.exceptions.http.not_found import NotFoundError
from app.api.v1.models.post.create_game import CreateGameModel
from app.api.v1.models.response.game import GameResponseModel
from app.api.v1.models.response.game_ticket import GameTicketResponseModel
from app.api.v1.security.authenticator import Authenticator
from app.api.v1.security.authorizer import Authorizer
from app.assets.redis.redis import GamesController
from app.assets.exceptions.player_already_in_game import PlayerAlreadyInGameError
from app.assets.exceptions.player_not_host import PlayerNotHostError
from app.assets.exceptions.player_not_in_game import PlayerNotInGameError
from app.assets.objects.game import Game
from app.database.models import User
from app.dependencies import games_controller_dependency

games_router: APIRouter = APIRouter(prefix="/games", tags=["Games"])


@games_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=GameResponseModel,
    dependencies=[Authorizer.has_permission(Permission.CREATE_GAMES)]
)
async def create_game(
        create_game_model: CreateGameModel,
        user: Annotated[User, Authenticator.get_user()],
        games_controller: Annotated[GamesController, Depends(games_controller_dependency)]
) -> GameResponseModel:
    if await games_controller.is_playing(user.id):
        raise PlayerAlreadyInGameError("You are already in game")

    game: Game = await games_controller.create_game(user.id, create_game_model.player_amount)
    return GameResponseModel.from_game(game)


@games_router.post(
    "/join",
    status_code=status.HTTP_200_OK,
    response_model=GameTicketResponseModel,
    dependencies=[Authorizer.has_permission(Permission.JOIN_GAMES)]
)
async def join_game(
        user: Annotated[User, Authenticator.get_user()],
        authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)],
        games_controller: Annotated[GamesController, Depends(games_controller_dependency)],
        code: Annotated[str, Query(min_length=6, max_length=6)] | None = None
) -> GameTicketResponseModel:
    if code is None:
        game: Game | None = await games_controller.get_game_by_player(user.id)
    else:
        game: Game | None = await games_controller.get_game_by_code(code)

    if game is None:
        raise NotFoundError("Game with provided code was not found")

    game_ticket: str = await authenticator.create_game_ticket(game.game_id, user.id)
    return GameTicketResponseModel(ticket=game_ticket)


@games_router.get(
    "/{game_id}",
    status_code=status.HTTP_200_OK,
    response_model=GameResponseModel,
    dependencies=[Authorizer.has_permission(Permission.VIEW_GAMES)]
)
async def get_game(
        game_id: UUID,
        games_controller: Annotated[GamesController, Depends(games_controller_dependency)]
) -> GameResponseModel:
    game: Game | None = await games_controller.get_game(game_id)

    if game is None:
        raise NotFoundError("Game with provided UUID was not found")

    return GameResponseModel.from_game(game)


@games_router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Authorizer.has_permission(Permission.REMOVE_GAMES)]
)
async def remove_game(
        game_id: UUID,
        games_controller: Annotated[GamesController, Depends(games_controller_dependency)]
) -> None:
    if not await games_controller.exists_game(game_id):
        raise NotFoundError("Game with provided UUID was not found")

    await games_controller.remove_game(game_id)


@games_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Authorizer.has_permission(Permission.REMOVE_OWN_GAMES)]
)
async def remove_own_game(
        user: Annotated[User, Authenticator.get_user()],
        games_controller: Annotated[GamesController, Depends(games_controller_dependency)]
) -> None:
    game: Game | None = await games_controller.get_game_by_player(user.id)

    if game is None:
        raise PlayerNotInGameError("You are not in game")
    if game.host_id != user.id:
        raise PlayerNotHostError("You are not a game host")

    await games_controller.remove_game(game.game_id)
