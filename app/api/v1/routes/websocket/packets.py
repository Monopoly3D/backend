import asyncio
from asyncio import Task, CancelledError
from inspect import getfullargspec
from typing import Dict, Any, Callable, Type, Annotated, Tuple, List, Sequence

from fastapi import APIRouter, Depends
from fastapi.routing import APIWebSocketRoute
from redis.asyncio import Redis
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.exceptions.websocket.internal_server_error import InternalServerError
from app.api.v1.exceptions.websocket.unknown_packet import UnknownPacketError
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.logging import logger
from app.api.v1.packets.base_client import ClientPacket
from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.server.error import ServerErrorPacket
from app.api.v1.security.authenticator import Authenticator
from app.assets.objects.connection import Connection
from app.assets.objects.connections import Connections
from app.assets.redis.games import GamesController
from app.database.database import Database
from app.database.models import User
from app.dependencies import games_controller_websocket, config_websocket, \
    redis_websocket, database_websocket
from config import Config


async def _dependencies(
        config: Annotated[Config, Depends(config_websocket)],
        database: Annotated[Database, Depends(database_websocket)],
        redis: Annotated[Redis, Depends(redis_websocket)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.websocket_dependency)],
        connections: Annotated[Connections, Depends(Connections.websocket_dependency)],
        games_controller: Annotated[GamesController, Depends(games_controller_websocket)],
        user: Annotated[User, Authenticator.get_websocket_user()]
) -> Dict[str, Any]:
    return {
        "config": config,
        "database": database,
        "redis": redis,
        "authenticator": authenticator,
        "connections": connections,
        "games_controller": games_controller,
        "user": user
    }


class PacketsRouter(APIRouter):
    _COMPLETED_TASK_REMOVAL_DELAY: int = 10

    def __init__(
            self,
            *,
            name: str,
            prefix: str,
            exceptions: Sequence[Type[Exception]] | None = None
    ) -> None:
        super().__init__(prefix=prefix)

        self._name = name
        self._handlers: Dict[Type[ClientPacket], Callable] = {}
        self._exceptions: Tuple[Type[Exception], ...] = (WebSocketError,) + tuple(exceptions) if exceptions is not None else ()

        self.add_api_websocket_route(
            "",
            self._handle_packets,
            self._name
        )

    def handle(
            self,
            packet: Type[ClientPacket]
    ) -> Callable:
        def decorator(func: Callable) -> None:
            self._handlers.update({packet: func})

        return decorator

    def authenticate(
            self,
            *,
            path: str | None = None
    ) -> Callable:
        def decorator(func: Callable) -> None:
            route_index: int | None = None

            for index, route in enumerate(self.routes):
                if not isinstance(route, APIWebSocketRoute):
                    continue

                if route.name == self._name:
                    route_index = index
                    break

            if route_index is not None:
                self.routes.pop(route_index)

            self.add_api_websocket_route(
                "" if path is None else path,
                self._handle_packets,
                self._name,
                dependencies=[Depends(func)]
            )

        return decorator

    async def _handle_packets(
            self,
            websocket: WebSocket,
            dp: Annotated[Dict[str, Any], Depends(_dependencies)]
    ) -> None:
        connection = Connection(websocket, dp.get("connections"))

        handle_tasks: List[Task] = []
        removal_task: Task = asyncio.create_task(self._always_remove_completed_tasks(handle_tasks))

        try:
            while True:
                packet: str = await connection.receive_text()
                handle_tasks.append(asyncio.create_task(self._handle_packet(packet, connection, **dp)))
        except (WebSocketDisconnect, RuntimeError, CancelledError):
            pass

        removal_task.cancel()

    async def _handle_packet(
            self,
            packet: str,
            connection: Connection,
            **kwargs
    ) -> None:
        try:
            try:
                packet: ClientPacket = ClientPacket.withdraw_packet(packet)

                if type(packet) not in self._handlers:
                    raise UnknownPacketError("Unknown packet")

                await self._execute_handler(self._handlers[type(packet)], packet, connection, **kwargs)
            except Exception as e:
                raise InternalServerError("Internal server error", e)
        except self._exceptions as exception:
            await connection.send_packet(ServerErrorPacket.from_error(exception))

            if isinstance(exception, InternalServerError):
                logger.exception(exception)
            else:
                logger.error(
                    f"(\'{connection.client.host}\', {connection.client.port}) "
                    f"WebSocket Error {exception.status_code}: {exception}"
                )

    async def _execute_handler(
            self,
            handler: Any,
            packet: ClientPacket,
            connection: Connection,
            **kwargs: Any
    ) -> None:
        handler_dependencies: Dict[str, Any] = await self._inject_dependencies(
            handler,
            packet=packet,
            connection=connection,
            **kwargs
        )

        prepared_args: Dict[str, Any] = self._prepare_args(
            handler,
            packet=packet,
            connection=connection,
            router=self,
            **handler_dependencies,
            **kwargs
        )

        response_packet: ServerPacket | None = await handler(**prepared_args)

        if response_packet is not None:
            await connection.send_packet(response_packet)

    async def _inject_dependencies(
            self,
            handler: Callable,
            **kwargs: Any
    ) -> Dict[str, Any]:
        handler_dependencies: Dict[str, Any] = {}

        if not hasattr(handler, "__annotations__"):
            return handler_dependencies

        for name, annotation in getattr(handler, "__annotations__").items():
            if not hasattr(annotation, "__metadata__"):
                continue

            func: Callable = annotation.__metadata__[0]

            func_dependencies: Dict[str, Any] = await self._inject_dependencies(
                func,
                **kwargs
            )

            prepared_args: Dict[str, Any] = self._prepare_args(
                func,
                **func_dependencies,
                **kwargs
            )

            handler_dependencies.update({name: await func(**prepared_args)})

        return handler_dependencies

    async def _always_remove_completed_tasks(
            self,
            handle_tasks: List[Task]
    ) -> None:
        while True:
            await asyncio.to_thread(self._remove_completed_tasks, handle_tasks=handle_tasks)
            await asyncio.sleep(self._COMPLETED_TASK_REMOVAL_DELAY)

    @staticmethod
    def _remove_completed_tasks(
            handle_tasks: List[Task]
    ) -> None:
        for index in range(len(handle_tasks) - 1, -1, -1):
            if handle_tasks[index].done():
                handle_tasks.pop(index)

    @staticmethod
    def _prepare_args(
            func: Callable,
            **kwargs: Any
    ) -> Dict[str, Any]:
        args: Tuple[str, ...] = tuple(getfullargspec(func)[0])

        return {
            k: arg for k, arg in kwargs.items()
            if k in args
        }
