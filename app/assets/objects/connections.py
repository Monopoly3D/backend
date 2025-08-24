from typing import Dict, TYPE_CHECKING, Optional
from uuid import UUID

from starlette.datastructures import Address
from starlette.requests import Request
from starlette.websockets import WebSocket

if TYPE_CHECKING:
    from app.assets.objects.connection import Connection


class Connections:
    def __init__(self) -> None:
        self._connections: Dict[UUID, 'Connection'] = {}
        self._addresses: Dict[Address, UUID] = {}

    async def add_connection(
            self,
            connection: 'Connection',
            user_id: UUID
    ) -> None:
        self._connections[user_id] = connection

        if connection.client is not None:
            self._addresses[connection.client] = user_id

    def get_connection(
            self,
            user_id: UUID
    ) -> Optional['Connection']:
        return self._connections.get(user_id)

    async def get_user_id(
            self,
            connection: 'Connection'
    ) -> UUID | None:
        if connection.client is not None:
            return self._addresses.get(connection.client)

    async def remove_connection(
            self,
            user_id: UUID
    ) -> None:
        connection: 'Connection' = self._connections.pop(user_id, None)
        if connection is not None and connection.client is not None:
            self._addresses.pop(connection.client, None)

    @staticmethod
    async def dependency(request: Request) -> 'Connections':
        return request.app.state.connections

    @staticmethod
    async def websocket_dependency(websocket: WebSocket) -> 'Connections':
        return websocket.app.state.connections
