from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import ValidationError
from redis.asyncio import Redis
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api.router import api_router
from app.api.v1.exceptions.api_error import APIError
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


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.exception_handler(ValidationError)
async def on_validation_error(request: Request, exception: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exception.errors()}
    )


@app.exception_handler(APIError)
async def on_api_error(request: Request, exception: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": str(exception)}
    )
