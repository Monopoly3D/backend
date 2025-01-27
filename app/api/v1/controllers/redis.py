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
        self.__redis: Redis = redis

    async def _create(
            self,
            key: str,
            value: Any
    ) -> None:
        try:
            data: str = json.dumps(value)
        except TypeError:
            raise Exception("Provided value is not JSON serializable")

        await self.__redis.set(f"monopoly:{key}", data)

    async def _get(
            self,
            key: str
    ) -> Any:
        serialized: str = await self.__redis.get(f"monopoly:{key}")

        try:
            return json.loads(serialized) if serialized is not None else None
        except ValueError:
            raise Exception("Provided value is not in a valid JSON format")

    async def _get_keys(
            self,
            *,
            pattern: str = ""
    ) -> Tuple[str, ...]:
        return tuple(await self.__redis.keys(f"*monopoly:{pattern}*"))

    async def _exists(
            self,
            key: str
    ) -> bool:
        return bool(await self.__redis.exists(f"monopoly:{key}"))

    async def _update(
            self,
            key: str,
            value: Any
    ) -> None:
        try:
            data: str = json.dumps(value)
        except TypeError:
            raise Exception("Provided value is not JSON serializable")

        if not await self.__redis.exists(f"monopoly:{key}"):
            raise Exception("Provided key does not exist")

        await self.__redis.set(f"monopoly:{key}", data)

    async def _remove(
            self,
            key: str
    ) -> None:
        await self.__redis.delete(f"monopoly:{key}")

    @classmethod
    async def dependency(
            cls,
            redis: Annotated[Redis, Depends(Dependency.redis)]
    ) -> 'RedisController':
        return cls(redis)
