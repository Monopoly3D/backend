from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.assets.objects.game_object import GameObject


@dataclass
class RedisObject(GameObject, ABC):
    @abstractmethod
    async def save(self) -> None: pass
