from inspect import getfullargspec
from typing import Dict, Any, Callable, Type, Annotated, Tuple

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
from app.api.v1.security.authenticator import Authenticator
from app.assets.exceptions.game_error import GameError
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
    _NAME = "packet_handler"

    def __init__(
            self,
            *,
            prefix: str
    ) -> None:
        super().__init__(prefix=prefix)
        self._handlers: Dict[Type[ClientPacket], Callable] = {}

        self.add_api_websocket_route(
            "",
            self._handle_packets,
            self._NAME
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

                if route.name == self._NAME:
                    route_index = index
                    break

            if route_index is not None:
                self.routes.pop(route_index)

            self.add_api_websocket_route(
                "" if path is None else path,
                self._handle_packets,
                self._NAME,
                dependencies=[Depends(func)]
            )

        return decorator

    async def _handle_packets(
            self,
            websocket: WebSocket,
            dp: Annotated[Dict[str, Any], Depends(_dependencies)]
    ) -> None:
        connection = Connection(websocket, dp.get("connections"))

        try:
            while True:
                packet: str = await connection.receive_text()
                await self._handle_packet(packet, connection, **dp)  # At some point it must create asyncio tasks
        except WebSocketDisconnect as e:
            logger.info(f"Closing connection. Status code: {e.code}, Reason: {e.reason}")
        except RuntimeError:
            pass

    async def _handle_packet(
            self,
            packet: str,
            connection: Connection,
            **kwargs
    ) -> None:
        try:
            packet: ClientPacket = ClientPacket.withdraw_packet(packet)

            if type(packet) not in self._handlers:
                raise UnknownPacketError("Unknown packet")

            await self._execute_handler(self._handlers[type(packet)], packet, connection, **kwargs)
        except GameError or WebSocketError as e:
            raise e
        except Exception as e:
            raise InternalServerError("Internal server error", e)

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
