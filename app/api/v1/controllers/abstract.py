from abc import ABC, abstractmethod
from typing import Any


class AbstractController(ABC):
    @abstractmethod
    async def _create(
            self,
            *args,
            **kwargs
    ) -> Any: pass

    @abstractmethod
    async def _get(
            self,
            *args,
            **kwargs
    ) -> Any: pass

    @abstractmethod
    async def _exists(
            self,
            *args,
            **kwargs
    ) -> Any: pass

    @abstractmethod
    async def _remove(
            self,
            *args,
            **kwargs
    ) -> Any: pass
