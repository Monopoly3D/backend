from abc import ABC, abstractmethod

from app.api.v1.controllers.redis import RedisController


class RedisObject(ABC):
    def __init__(
            self,
            redis_key: str,
            controller: RedisController
    ) -> None:
        self.__redis_key = redis_key
        self.__controller = controller

    @abstractmethod
    def to_json(self) -> None:
        pass

    async def save(self) -> None:
        await self.__controller.set(self.__redis_key, self.to_json())
