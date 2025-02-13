from fastapi import FastAPI
from redis.asyncio import Redis
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.controllers.users import UsersController
from config import Config


class Dependency:
    @staticmethod
    async def inject(
            fastapi_app: FastAPI,
            config: Config,
            database,
            redis: Redis,
            connections: ConnectionsController
    ) -> None:
        fastapi_app.state.config = config
        fastapi_app.state.database = database
        fastapi_app.state.redis = redis
        fastapi_app.state.connections = connections

        users_controller = UsersController(redis)
        games_controller = GamesController(redis)
        await users_controller.retrieve_users()
        await games_controller.retrieve_games(connections)

        fastapi_app.state.users_controller = users_controller
        fastapi_app.state.games_controller = games_controller

    @staticmethod
    async def config(request: Request) -> Config:
        return request.app.state.config

    @staticmethod
    async def database(request: Request) -> None:
        return request.app.state.database

    @staticmethod
    async def redis(request: Request) -> Redis:
        return request.app.state.redis

    @staticmethod
    async def users_controller(request: Request) -> 'UsersController':
        return request.app.state.users_controller

    @staticmethod
    async def games_controller(request: Request) -> 'GamesController':
        return request.app.state.games_controller

    @staticmethod
    async def config_websocket(websocket: WebSocket) -> Config:
        return websocket.app.state.config

    @staticmethod
    async def database_websocket(websocket: WebSocket) -> None:
        return websocket.app.state.database

    @staticmethod
    async def redis_websocket(websocket: WebSocket) -> Redis:
        return websocket.app.state.redis

    @staticmethod
    async def users_controller_websocket(websocket: WebSocket) -> 'UsersController':
        return websocket.app.state.users_controller

    @staticmethod
    async def games_controller_websocket(websocket: WebSocket) -> 'GamesController':
        return websocket.app.state.games_controller
