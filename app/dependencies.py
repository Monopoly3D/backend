from fastapi import FastAPI
from redis.asyncio import Redis
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from config import Config


class Dependency:
    @staticmethod
    def inject(
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
    async def config_websocket(websocket: WebSocket) -> Config:
        return websocket.app.state.config

    @staticmethod
    async def database_websocket(websocket: WebSocket) -> None:
        return websocket.app.state.database

    @staticmethod
    async def redis_websocket(websocket: WebSocket) -> Redis:
        return websocket.app.state.redis
