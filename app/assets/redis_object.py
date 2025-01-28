from abc import ABC, abstractmethod
from typing import Any, Dict


class RedisObject(ABC):
    @abstractmethod
    def __init__(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None: pass

    @abstractmethod
    async def save(self) -> None: pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]: pass
