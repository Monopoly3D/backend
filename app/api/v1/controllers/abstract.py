from abc import ABC, abstractmethod
from typing import Any


class AbstractController(ABC):
    @abstractmethod
    async def create(
            self,
            *args,
            **kwargs
    ) -> Any: pass

    @abstractmethod
    async def get(
            self,
            *args,
            **kwargs
    ) -> Any: pass

    @abstractmethod
    async def exists(
            self,
            *args,
            **kwargs
    ) -> Any: pass

    @abstractmethod
    async def remove(
            self,
            *args,
            **kwargs
    ) -> Any: pass
