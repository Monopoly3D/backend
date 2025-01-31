from abc import ABC, abstractmethod
from typing import Any


class AbstractPacketsRouter(ABC):
    @abstractmethod
    async def handle_packets(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None:
        pass

    @abstractmethod
    def handle(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None:
        pass
