import json
from typing import Annotated, Any, Tuple

from fastapi import Depends
from redis import Redis

from app.api.v1.controllers.abstract import AbstractController
from app.dependencies import Dependency


class RedisController(AbstractController):
    def __init__(
            self,
            redis: Redis
    ) -> None:
        self._redis: Redis = redis

    @staticmethod
    async def dependency() -> Depends:
        async def __dependency(redis: Annotated[Redis, Depends(Dependency.redis)]) -> RedisController:
            return RedisController(redis)

        return Depends(__dependency)

    async def create(
            self,
            key: str,
            value: Any
    ) -> None:
        await self._redis.set(f"monopoly:{key}", json.dumps(value))

    async def get(
            self,
            key: str
    ) -> Any:
        serialized: str = await self._redis.get(f"monopoly:{key}")
        return json.loads(serialized) if serialized is not None else None

    async def get_keys(
            self,
            *,
            pattern: str = ""
    ) -> Tuple[str, ...]:
        return tuple(await self._redis.keys(f"*monopoly:{pattern}*"))

    async def exists(
            self,
            key: str
    ) -> bool:
        return bool(await self._redis.exists(f"monopoly:{key}"))

    async def remove(
            self,
            key: str
    ) -> None:
        await self._redis.delete(f"monopoly:{key}")
