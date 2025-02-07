import asyncio
from inspect import getfullargspec
from typing import Dict, Any, Callable, Type, Annotated, Tuple, TypeVar
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.controllers.users import UsersController
from app.api.v1.exceptions.websocket.internal_server_error import InternalServerError
from app.api.v1.exceptions.websocket.packet_timeout import PacketTimeoutError
from app.api.v1.exceptions.websocket.unknown_packet import UnknownPacketError
from app.api.v1.exceptions.websocket.websocket_error import WebSocketError
from app.api.v1.logging import logger
from app.api.v1.packets.base_client import ClientPacket
from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.routes.websocket.abstract_packets import AbstractPacketsRouter
from app.api.v1.security.authenticator import Authenticator
from app.assets.objects.user import User
from app.dependencies import Dependency
from config import Config

T = TypeVar("T", bound=ClientPacket)


async def dependencies(
        config: Annotated[Config, Depends(Dependency.config_websocket)],
        redis: Annotated[Redis, Depends(Dependency.redis_websocket)],
        authenticator: Annotated[Authenticator, Depends(Authenticator.websocket_dependency)],
        connections: Annotated[ConnectionsController, Depends(ConnectionsController.websocket_dependency)],
        users_controller: Annotated[UsersController, Depends(Dependency.users_controller_websocket)],
        games_controller: Annotated[GamesController, Depends(Dependency.games_controller_websocket)],
        user: Annotated[User, Authenticator.get_websocket_user()]
) -> Dict[str, Any]:
    return {
        "config": config,
        "redis": redis,
        "authenticator": authenticator,
        "connections": connections,
        "users_controller": users_controller,
        "games_controller": games_controller,
        "user": user
    }


class PacketsRouter(APIRouter, AbstractPacketsRouter):
    def __init__(
            self,
            *,
            prefix: str
    ) -> None:
        super().__init__(prefix=prefix)
        self.__handlers: Dict[Type[ClientPacket], Callable] = {}
        self.__awaiting: Dict[Type[ClientPacket], Dict[UUID, Any]] = {}

        self.add_api_websocket_route(
            "/",
            self.handle_packets,
            dependencies=[Authenticator.authenticate_websocket_dependency()]
        )

    def handle(
            self,
            packet: Type[ClientPacket]
    ) -> Callable:
        def decorator(func: Callable) -> None:
            self.__handlers.update({packet: func})

        return decorator

    async def await_packet(
            self,
            packet: Type[T],
            *,
            timeout: float = 300,
            polling_timeout: float = 0.1
    ) -> T:
        if packet not in self.__awaiting:
            self.__awaiting[packet] = {}

        awaiting_uuid: UUID = uuid4()

        self.__awaiting[packet][awaiting_uuid] = None

        for _ in range(int(timeout / polling_timeout)):
            awaiting: Any = self.__awaiting[packet][awaiting_uuid]

            if awaiting is not None:
                self.__awaiting[packet].pop(awaiting_uuid)
                if not self.__awaiting[packet]:
                    self.__awaiting.pop(packet)

                return awaiting

            await asyncio.sleep(polling_timeout)

        raise PacketTimeoutError("Awaited too long to retrieve packet")

    async def handle_packets(
            self,
            websocket: WebSocket,
            dp: Annotated[Dict[str, Any], Depends(dependencies)]
    ) -> None:
        try:
            while True:
                packet: str = await websocket.receive_text()
                asyncio.create_task(self.__handle_packet(packet, websocket, **dp))
        except WebSocketDisconnect as e:
            logger.info(f"Closing connection. Status code: {e.code}, Reason: {e.reason}")

    async def __handle_packet(
            self,
            packet: str,
            websocket: WebSocket,
            **kwargs
    ) -> None:
        try:
            packet: ClientPacket = ClientPacket.withdraw_packet(packet)
            is_awaiting: bool = False

            for awaiting_packet, awaiting in self.__awaiting.items():
                if awaiting_packet == type(packet):
                    self.__awaiting[awaiting_packet] = {uid: packet for uid in self.__awaiting[awaiting_packet].keys()}
                    is_awaiting = True

            if is_awaiting:
                return

            if type(packet) not in self.__handlers:
                raise UnknownPacketError("Unknown packet")

            await self.__execute_handler(self.__handlers[type(packet)], packet, websocket, **kwargs)
        except WebSocketError as e:
            raise e
        except Exception as e:
            raise InternalServerError("Internal server error", e)

    async def __execute_handler(
            self,
            handler: Any,
            packet: ClientPacket,
            websocket: WebSocket,
            **kwargs: Any
    ) -> None:
        handler_dependencies: Dict[str, Any] = await self.__inject_dependencies(
            handler,
            packet=packet,
            websocket=websocket,
            **kwargs
        )

        prepared_args: Dict[str, Any] = self.__prepare_args(
            handler,
            packet=packet,
            websocket=websocket,
            router=self,
            **handler_dependencies,
            **kwargs
        )

        response_packet: ServerPacket | None = await handler(**prepared_args)

        if response_packet is not None:
            await websocket.send_text(response_packet.pack())

    async def __inject_dependencies(
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

            func_dependencies: Dict[str, Any] = await self.__inject_dependencies(
                func,
                **kwargs
            )

            prepared_args: Dict[str, Any] = self.__prepare_args(
                func,
                **func_dependencies,
                **kwargs
            )

            handler_dependencies.update({name: await func(**prepared_args)})

        return handler_dependencies

    @staticmethod
    def __prepare_args(
            func: Callable,
            **kwargs: Any
    ) -> Dict[str, Any]:
        args: Tuple[str, ...] = tuple(getfullargspec(func)[0])

        return {
            k: arg for k, arg in kwargs.items()
            if k in args
        }
