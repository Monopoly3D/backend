from abc import ABC, abstractmethod
from typing import Any

from starlette.websockets import WebSocket


class AbstractPacketsRouter(ABC):
    @abstractmethod
    async def handle_packets(
            self,
            websocket: WebSocket
    ) -> None:
        pass

    @abstractmethod
    def handle(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None:
        pass
