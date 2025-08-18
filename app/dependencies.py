from typing import Annotated, AsyncGenerator

from fastapi import Depends
from fastapi_mail import FastMail
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.assets.controllers.redis.games import GamesController
from app.assets.controllers.s3.profile_pictures import ProfilePicturesController
from app.database.database import Database
from config import Config


async def config_dependency(request: Request) -> Config:
    return request.app.state.config


async def database_dependency(request: Request) -> Database:
    return request.app.state.database


async def database_session(
        database: Annotated[Database, Depends(database_dependency)]
) -> AsyncGenerator[AsyncSession, None]:
    async with database.session_maker() as session:
        yield session


async def redis_dependency(request: Request) -> Redis:
    return request.app.state.redis


async def games_controller_dependency(request: Request) -> GamesController:
    return request.app.state.games_controller


async def profile_pictures_controller_dependency(request: Request) -> ProfilePicturesController:
    return request.app.state.profile_pictures_controller


async def no_reply_email_dependency(request: Request) -> FastMail:
    return FastMail(request.app.state.no_reply_email_config)


async def config_websocket(websocket: WebSocket) -> Config:
    return websocket.app.state.config


async def database_websocket(websocket: WebSocket) -> Database:
    return websocket.app.state.database


async def database_websocket_session(
        database: Annotated[Database, Depends(database_websocket)]
) -> None:
    async with database.session_maker() as session:
        yield session


async def redis_websocket(websocket: WebSocket) -> Redis:
    return websocket.app.state.redis


async def games_controller_websocket(websocket: WebSocket) -> GamesController:
    return websocket.app.state.games_controller


async def profile_pictures_controller_websocket(websocket: WebSocket) -> ProfilePicturesController:
    return websocket.app.state.profile_pictures_controller
