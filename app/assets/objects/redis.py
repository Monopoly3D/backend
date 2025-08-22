from abc import ABC, abstractmethod

from pydantic.dataclasses import dataclass

from app.assets.objects.object import GameObject


@dataclass
class RedisObject(GameObject, ABC):
    @abstractmethod
    async def save(self) -> None: pass

    @abstractmethod
    async def clear(self) -> None: pass
