from fastapi import FastAPI
from redis.asyncio import Redis
from starlette.requests import Request

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

    @staticmethod
    async def config(request: Request) -> Config:
        return request.app.state.config

    @staticmethod
    async def database(request: Request) -> None:
        return request.app.state.database

    @staticmethod
    async def redis(request: Request) -> Redis:
        return request.app.state.redis
