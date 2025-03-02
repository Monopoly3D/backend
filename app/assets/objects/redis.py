from abc import ABC

from app.api.v1.controllers.redis import RedisController
from app.assets.objects.game_object import GameObject


class RedisObject(GameObject, ABC):
    def __init__(
            self,
            redis_key: str,
            controller: RedisController
    ) -> None:
        self.__redis_key = redis_key
        self.__controller = controller

    async def save(self) -> None:
        await self.__controller.set(self.__redis_key, self.to_json())
