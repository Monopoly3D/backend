from starlette.websockets import WebSocket

from app.api.v1.routes.packets.abstract import AbstractPacketsRouter


class GamesPacketsRouter(AbstractPacketsRouter):
    def __init__(self):
        pass

    async def handle(self, websocket: WebSocket) -> None:
        await websocket.accept()




games_packets_router = GamesPacketsRouter()
