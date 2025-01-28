from abc import ABC, abstractmethod


class RedisObject(ABC):
    @abstractmethod
    async def save(self) -> None: pass
