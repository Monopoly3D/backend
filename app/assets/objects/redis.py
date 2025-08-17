from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

from app.api.v1.controllers.redis import RedisController
from app.assets.objects.game_object import GameObject


@dataclass
class RedisObject(GameObject, ABC):
    @abstractmethod
    async def save(self) -> None: pass

    @classmethod
    @abstractmethod
    def from_json(cls, *args, **kwargs) -> Any:
        pass
