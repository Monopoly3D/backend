from typing import Annotated, AsyncGenerator

from fastapi import FastAPI, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.database.database import Database
from config import Config


async def inject(
        fastapi_app: FastAPI,
        config: Config,
        database: Database,
        redis: Redis,
        connections: ConnectionsController
) -> None:
    fastapi_app.state.config = config
    fastapi_app.state.database = database
    fastapi_app.state.redis = redis
    fastapi_app.state.connections = connections

    games_controller = GamesController(redis)
    await games_controller.retrieve_games(connections)

    fastapi_app.state.games_controller = games_controller


async def config_dependency(request: Request) -> Config:
    return request.app.state.config


async def database_dependency(request: Request) -> None:
    return request.app.state.database


async def database_session(
        database: Annotated[Database, Depends(database_dependency)]
) -> AsyncGenerator[AsyncSession, None]:
    async with database.session_maker() as session:
        yield session


async def redis_dependency(request: Request) -> Redis:
    return request.app.state.redis


async def games_controller_dependency(request: Request) -> 'GamesController':
    return request.app.state.games_controller


async def config_websocket(websocket: WebSocket) -> Config:
    return websocket.app.state.config


async def database_websocket(websocket: WebSocket) -> None:
    return websocket.app.state.database


async def database_websocket_session(
        database: Annotated[Database, Depends(database_websocket)]
) -> None:
    async with database.session_maker() as session:
        yield session


async def redis_websocket(websocket: WebSocket) -> Redis:
    return websocket.app.state.redis


async def games_controller_websocket(websocket: WebSocket) -> 'GamesController':
    return websocket.app.state.games_controller
