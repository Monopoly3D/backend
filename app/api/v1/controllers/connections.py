from typing import Dict
from uuid import UUID

from redis.asyncio import Redis
from starlette.datastructures import Address
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.api.v1.controllers.redis import RedisController


class ConnectionsController(RedisController):
    REDIS_KEY = "connections"

    def __init__(
            self,
            redis: Redis
    ) -> None:
        super().__init__(redis)
        self.connections: Dict[UUID, WebSocket] = {}

    async def prepare(self) -> None:
        await self.set(self.REDIS_KEY, {})

    async def add_connection(
            self,
            websocket: WebSocket,
            user_id: UUID
    ) -> None:
        address: Address | None = websocket.client

        if address is None:
            return

        connections: Dict[str, str] | None = await self.get(self.REDIS_KEY)

        if connections is None:
            connections: Dict[str, str] = {}

        connections[self.__address_to_str(address)] = str(user_id)
        await self.set(self.REDIS_KEY, connections)

        self.connections[user_id] = websocket

    async def get_user_id(
            self,
            websocket: WebSocket
    ) -> UUID | None:
        address: Address | None = websocket.client

        if address is None:
            return

        connections: Dict[str, str] | None = await self.get(self.REDIS_KEY)

        if connections is None:
            return

        if self.__address_to_str(address) in connections:
            return UUID(connections[self.__address_to_str(address)])

    async def remove_connection(
            self,
            user_id: UUID
    ) -> None:
        connection: WebSocket | None = self.connections.get(user_id)

        if connection is None:
            return

        address: Address | None = connection.client

        if address is not None:
            connections: Dict[str, str] | None = await self.get(self.REDIS_KEY)

            if connections is not None and self.__address_to_str(connection.client) in connections:
                connections.pop(self.__address_to_str(address))
            else:
                connections: Dict[str, str] = {}

            await self.set(self.REDIS_KEY, connections)

        try:
            await connection.close()
        except RuntimeError:
            pass

        self.connections.pop(user_id)

    @staticmethod
    def __address_to_str(address: Address) -> str:
        return f"{address[0]}:{address[1]}"

    @staticmethod
    async def dependency(request: Request) -> 'ConnectionsController':
        return request.app.state.connections

    @staticmethod
    async def websocket_dependency(websocket: WebSocket) -> 'ConnectionsController':
        return websocket.app.state.connections
