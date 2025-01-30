from abc import ABC, abstractmethod

from starlette.websockets import WebSocket


class AbstractPacketsRouter(ABC):
    @abstractmethod
    async def handle(
            self,
            websocket: WebSocket
    ) -> None:
        pass
