from typing import Dict
from uuid import UUID

from starlette.datastructures import Address
from starlette.requests import Request
from starlette.websockets import WebSocket


class Connections:
    def __init__(self) -> None:
        self._connections: Dict[UUID, WebSocket] = {}
        self._addresses: Dict[Address, UUID] = {}

    async def add_connection(
            self,
            websocket: WebSocket,
            user_id: UUID
    ) -> None:
        self._connections[user_id] = websocket

        if websocket.client is not None:
            self._addresses[websocket.client] = user_id

    def get_connection(
            self,
            user_id: UUID
    ) -> WebSocket | None:
        return self._connections.get(user_id)

    async def get_user_id(
            self,
            websocket: WebSocket
    ) -> UUID | None:
        if websocket.client is not None:
            return self._addresses.get(websocket.client)

    async def remove_connection(
            self,
            user_id: UUID
    ) -> None:
        websocket: WebSocket = self._connections.pop(user_id, None)
        if websocket is not None and websocket.client is not None:
            self._addresses.pop(websocket.client, None)

    @staticmethod
    async def dependency(request: Request) -> 'Connections':
        return request.app.state.connections

    @staticmethod
    async def websocket_dependency(websocket: WebSocket) -> 'Connections':
        return websocket.app.state.connections
