from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import ValidationError
from redis.asyncio import Redis
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket

from app.api.router import api_router
from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.exceptions.http.http_error import HTTPError
from app.api.v1.exceptions.websocket.internal_server_error import InternalServerError
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.logging import logger
from app.api.v1.packets.server.error import ServerErrorPacket
from app.assets.exceptions.game_error import GameError
from app.database.database import Database
from config import Config

config: Config = Config(_env_file=".env")
database: Database = Database.from_dsn(config.database_dsn.get_secret_value())
redis: Redis = Redis.from_url(config.redis_dsn.get_secret_value())
connections: ConnectionsController = ConnectionsController()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await fastapi_app.state.games_controller.retrieve_games(connections)
    yield
    await redis.aclose()


app = FastAPI(lifespan=lifespan)

app.state.config = config
app.state.database = database
app.state.redis = redis
app.state.connections = connections
app.state.games_controller = GamesController(redis)

app.include_router(api_router)


@app.exception_handler(ValidationError)
async def on_validation_error(request: Request, exception: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exception.errors()}
    )


@app.exception_handler(HTTPError)
async def on_http_error(request: Request, exception: HTTPError) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": str(exception)}
    )


@app.exception_handler(GameError)
async def on_game_error(websocket: WebSocket, exception: GameError) -> None:
    try:
        await websocket.send_text(ServerErrorPacket.from_error(exception).pack())

        if isinstance(exception, InternalServerError):
            raise exception.error
        else:
            logger.error(
                f"(\'{websocket.client.host}\', {websocket.client.port}) "
                f"Game error {exception.status_code}: {exception}"
            )
    except RuntimeError:
        pass


@app.exception_handler(WebSocketError)
async def on_websocket_error(websocket: WebSocket, exception: WebSocketError) -> None:
    try:
        await websocket.send_text(ServerErrorPacket.from_error(exception).pack())

        if isinstance(exception, InternalServerError):
            raise exception.error
        else:
            logger.error(
                f"(\'{websocket.client.host}\', {websocket.client.port}) "
                f"WebSocket error {exception.status_code}: {exception}"
            )
    except RuntimeError:
        pass


@app.exception_handler(Exception)
async def on_server_error(request: Request, exception: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exception)}
    )
