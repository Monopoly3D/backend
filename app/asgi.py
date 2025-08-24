import asyncio
from contextlib import asynccontextmanager
from typing import Any, Annotated

from fastapi import FastAPI
from pydantic import ValidationError
from redis.asyncio import Redis
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket

from app.api.router import api_router, ws_router
from app.api.v1.assets.email_sender import EmailSender
from app.api.v1.exceptions.http.http_error import HTTPError
from app.api.v1.exceptions.websocket.internal_server_error import InternalServerError
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.logging import logger
from app.api.v1.packets.server.error import ServerErrorPacket
from app.assets.exceptions.game_error import GameError
from app.assets.objects.connection import Connection
from app.assets.objects.connections import Connections
from app.assets.redis.games import GamesController
from app.assets.s3.abstract import S3Config
from app.assets.s3.profile_pictures import ProfilePicturesController
from app.database.database import Database
from config import Config

config = Config(_env_file=".env")


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    database = Database.from_dsn(
        config.database_dsn.get_secret_value()
    )
    redis = Redis.from_url(
        config.redis_dsn.get_secret_value()
    )
    s3_config = S3Config(
        config.s3_dsn.get_secret_value(),
        config.s3_region,
        config.s3_username.get_secret_value(),
        config.s3_password.get_secret_value()
    )

    fastapi_app.state.config = config
    fastapi_app.state.database = database
    fastapi_app.state.redis = redis
    fastapi_app.state.connections = Connections()
    fastapi_app.state.games_controller = GamesController(redis)
    fastapi_app.state.profile_pictures_controller = ProfilePicturesController(s3_config)

    fastapi_app.state.email_sender = EmailSender(
        config.email_name.get_secret_value(),
        config.email_password.get_secret_value(),
        config.smtp_host,
        config.smtp_port
    )

    yield

    await redis.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
        "https://localhost:8000",
        "ws://localhost:8000",
        "wss://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router)
app.include_router(ws_router)


@app.exception_handler(GameError)
async def on_game_error(request: Request | WebSocket, exception: GameError) -> Any:
    if isinstance(request, Request):
        raise HTTPError(str(exception))
    elif isinstance(request, WebSocket):
        raise WebSocketError(str(exception))


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


@app.exception_handler(WebSocketError)
async def on_websocket_error(
        websocket: WebSocket,
        exception: WebSocketError,
        connections: Annotated[Connections, Connections.dependency],
) -> None:
    connection = Connection(websocket, connections)
    await connection.send_packet(ServerErrorPacket.from_error(exception))

    if isinstance(exception, InternalServerError):
        raise exception.error
    else:
        logger.error(
            f"(\'{connection.client.host}\', {connection.client.port}) "
            f"WebSocket Error {exception.status_code}: {exception}"
        )


@app.exception_handler(Exception)
async def on_server_error(
        request: Request,
        exception: Exception
) -> JSONResponse:
    logger.exception(exception)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"}
    )
