from typing import Dict
from uuid import UUID

from starlette.datastructures import Address
from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.__connections: Dict[Address, UUID] = {}

    async def add_connection(
            self,
            address: Address,
            user_id: UUID
    ) -> None:
        if address is not None:
            self.__connections[address] = user_id

    async def get_user_id(
            self,
            address: Address
    ) -> UUID | None:
        return self.__connections.get(address)

    @staticmethod
    async def dependency(request: WebSocket) -> 'ConnectionManager':
        return request.app.state.connection_manager

    @staticmethod
    async def websocket_dependency(websocket: WebSocket) -> 'ConnectionManager':
        return websocket.app.state.connection_manager
