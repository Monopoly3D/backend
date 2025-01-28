from abc import ABC, abstractmethod
from typing import Any


class RedisObject(ABC):
    @abstractmethod
    def __init__(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None: pass

    @abstractmethod
    async def save(self) -> None: pass
