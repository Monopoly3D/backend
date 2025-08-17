from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.api.v1.controllers.redis import RedisController
from app.assets.objects.game_object import GameObject


@dataclass
class RedisObject(GameObject, ABC):
    def __init__(
            self,
            redis_key: str,
            controller: RedisController
    ) -> None:
        self._redis_key = redis_key
        self._controller = controller

    @abstractmethod
    async def save(self) -> None: pass
