from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_mail import ConnectionConfig
from pydantic import ValidationError
from redis.asyncio import Redis
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket

from app.api.router import api_router
from app.api.v1.controllers.connections import ConnectionsController
from app.assets.controllers.games import GamesController
from app.api.v1.exceptions.http.http_error import HTTPError
from app.api.v1.exceptions.websocket.internal_server_error import InternalServerError
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.logging import logger
from app.api.v1.packets.server.error import ServerErrorPacket
from app.assets.exceptions.game_error import GameError
from app.database.database import Database
from config import Config


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    config: Config = Config(_env_file=".env")
    database: Database = Database.from_dsn(config.database_dsn.get_secret_value())
    redis: Redis = Redis.from_url(config.redis_dsn.get_secret_value())
    connections: ConnectionsController = ConnectionsController()

    fastapi_app.state.config = config
    fastapi_app.state.database = database
    fastapi_app.state.redis = redis
    fastapi_app.state.connections = connections
    fastapi_app.state.games_controller = GamesController(redis)

    fastapi_app.state.no_reply_email_config = ConnectionConfig(
        MAIL_USERNAME=config.no_reply_email_sender.get_secret_value(),
        MAIL_PASSWORD=config.no_reply_email_password,
        MAIL_FROM=config.no_reply_email_sender.get_secret_value(),
        MAIL_SERVER=config.smtp_host,
        MAIL_PORT=config.smtp_port,
        MAIL_SSL_TLS=True,
        MAIL_STARTTLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

    yield

    await redis.aclose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
