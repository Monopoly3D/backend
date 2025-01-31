from fastapi import FastAPI
from redis.asyncio import Redis
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.api.v1.controllers.games import GamesController
from app.api.v1.controllers.users import UsersController
from app.api.v1.security.authenticator import Authenticator
from config import Config


class Dependency:
    @staticmethod
    def inject(
            fastapi_app: FastAPI,
            config: Config,
            database,
            redis: Redis
    ) -> None:
        fastapi_app.state.config = config
        fastapi_app.state.database = database
        fastapi_app.state.redis = redis

        fastapi_app.state.authenticator = Authenticator(
            jwt_key=config.jwt_key.get_secret_value(),
            jwt_algorithm=config.jwt_algorithm
        )

        fastapi_app.state.users_controller = UsersController(redis)
        fastapi_app.state.games_controller = GamesController(redis)

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
    async def authenticator(request: Request) -> Authenticator:
        return request.app.state.authenticator

    @staticmethod
    async def users_controller(request: Request) -> UsersController:
        return request.app.state.users_controller

    @staticmethod
    async def games_controller(request: Request) -> GamesController:
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
    async def users_controller_websocket(websocket: WebSocket) -> UsersController:
        return websocket.app.state.users_controller

    @staticmethod
    async def games_controller_websocket(websocket: WebSocket) -> GamesController:
        return websocket.app.state.games_controller
