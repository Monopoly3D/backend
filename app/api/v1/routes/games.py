from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.websockets import WebSocket

from app.api.v1.controllers.games import GamesController
from app.api.v1.models.response.game import GameResponseModel
from app.api.v1.packets.client.ping import ClientPingPacket
from app.api.v1.packets.server.ping import ServerPingPacket
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


@games_router.websocket("/ping")
async def ping(websocket: WebSocket) -> None:
    await websocket.accept()

    while True:
        data: str = await websocket.receive_text()
        packet: ClientPingPacket = ClientPingPacket.unpack(data)

        print(f"Received request: {packet.request}")

        await websocket.send_text(ServerPingPacket(packet.request).pack(to_string=True))
