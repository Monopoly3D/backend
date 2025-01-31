import json
from typing import Any, Tuple

from redis import Redis


class RedisController:
    REDIS_KEY: str

    def __init__(
            self,
            redis: Redis
    ) -> None:
        self._redis: Redis = redis

    async def set(
            self,
            key: str,
            value: Any,
            *,
            exact_key: bool = False
    ) -> None:
        await self._redis.set(key if exact_key else f"monopoly:{key}", json.dumps(value))

    async def get(
            self,
            key: str,
            *,
            exact_key: bool = False
    ) -> Any:
        serialized: str = await self._redis.get(key if exact_key else f"monopoly:{key}")
        return json.loads(serialized) if serialized is not None else None

    async def get_keys(
            self,
            *,
            pattern: str = "",
            exact_pattern: bool = False
    ) -> Tuple[str, ...]:
        return tuple(await self._redis.keys(f"*{pattern}*" if exact_pattern else f"*monopoly:{pattern}*"))

    async def exists(
            self,
            key: str,
            *,
            exact_key: bool = False
    ) -> bool:
        return bool(await self._redis.exists(key if exact_key else f"monopoly:{key}"))

    async def remove(
            self,
            key: str,
            *,
            exact_key: bool = False
    ) -> None:
        await self._redis.delete(key if exact_key else f"monopoly:{key}")
