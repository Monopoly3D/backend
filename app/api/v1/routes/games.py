from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.websockets import WebSocket

from app.api.v1.controllers.games import GamesController
from app.api.v1.models.response.game import GameResponseModel
from app.api.v1.routes.packets.games import games_packets_router
from app.assets.game import Game

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


@games_router.websocket("/")
async def on_games_websocket(websocket: WebSocket) -> None:
    await games_packets_router.handle(websocket)
