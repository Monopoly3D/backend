from typing import Dict
from uuid import UUID

from starlette.datastructures import Address
from starlette.requests import Request
from starlette.websockets import WebSocket


class ConnectionsController:
    def __init__(self) -> None:
        self.connections: Dict[UUID, WebSocket] = {}
        self.addresses: Dict[Address, UUID] = {}

    async def add_connection(
            self,
            websocket: WebSocket,
            user_id: UUID
    ) -> None:
        self.connections[user_id] = websocket

        if websocket.client is not None:
            self.addresses[websocket.client] = user_id

    def get_connection(
            self,
            user_id: UUID
    ) -> WebSocket:
        return self.connections.get(user_id)

    async def get_user_id(
            self,
            websocket: WebSocket
    ) -> UUID | None:
        if websocket.client is not None:
            return self.addresses.get(websocket.client)

    async def remove_connection(
            self,
            user_id: UUID
    ) -> None:
        websocket: WebSocket = self.connections.pop(user_id, None)
        if websocket is not None and websocket.client is not None:
            self.addresses.pop(websocket.client, None)

    @staticmethod
    async def dependency(request: Request) -> 'ConnectionsController':
        return request.app.state.connections

    @staticmethod
    async def websocket_dependency(websocket: WebSocket) -> 'ConnectionsController':
        return websocket.app.state.connections
