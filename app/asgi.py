from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.api.router import api_router
from app.dependencies import Dependency
from config import Config

config: Config = Config(_env_file=".env")


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    database = None
    redis: Redis = Redis.from_url(config.redis_dsn.get_secret_value())

    Dependency.inject(
        fastapi_app,
        database,
        redis
    )

    yield

    await redis.aclose()


app = FastAPI()
app.include_router(api_router)
