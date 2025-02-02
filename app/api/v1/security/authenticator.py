import asyncio
from datetime import datetime, timedelta
from typing import Dict, Annotated
from uuid import UUID

from fastapi import Depends, Header
from jwt import encode, decode, InvalidTokenError, DecodeError, ExpiredSignatureError, InvalidSignatureError
from pytz import utc
from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.users import UsersController
from app.api.v1.exceptions.http.invalid_access_token import InvalidAccessTokenError
from app.api.v1.exceptions.http.invalid_credentials import InvalidCredentialsError
from app.api.v1.exceptions.http.invalid_packet import InvalidPacketError
from app.api.v1.exceptions.websocket.not_authenticated_address import NotAuthenticatedAddressError
from app.api.v1.packets.client.auth import ClientAuthPacket
from app.api.v1.packets.server.auth import ServerAuthPacket
from app.assets.objects.user import User
from app.dependencies import Dependency
from config import Config


class Authenticator:
    ACCESS_TOKEN_EXPIRE = timedelta(days=1)
    TICKET_EXPIRE = timedelta(days=1)

    def __init__(
            self,
            *,
            jwt_key: str,
            jwt_algorithm: str
    ) -> None:
        self.__jwt_key = jwt_key
        self.__jwt_algorithm = jwt_algorithm

    def create_access_token(
            self,
            user_id: UUID
    ) -> str:
        return encode(
            {
                "id": str(user_id),
                "exp": datetime.now(utc) + self.ACCESS_TOKEN_EXPIRE,
                "mode": "access"
            },
            self.__jwt_key,
            self.__jwt_algorithm
        )

    def create_ticket(
            self,
            user_id: UUID
    ) -> str:
        return encode(
            {
                "id": str(user_id),
                "exp": datetime.now(utc) + self.TICKET_EXPIRE,
                "mode": "ticket"
            },
            self.__jwt_key,
            self.__jwt_algorithm
        )

    def decode_access_token(
            self,
            access_token: str
    ) -> Dict[str, str]:
        try:
            access_token: Dict[str, str] = decode(
                access_token,
                self.__jwt_key,
                [self.__jwt_algorithm]
            )
        except InvalidTokenError:
            raise InvalidAccessTokenError("Provided access token is invalid or expired")

        if "id" not in access_token or "mode" not in access_token:
            raise InvalidAccessTokenError("Provided access token is invalid")

        if access_token.get("mode") != "access":
            raise InvalidAccessTokenError("Provided access token is invalid")

        return access_token

    def decode_ticket(
            self,
            ticket: str
    ) -> Dict[str, str]:
        try:
            ticket: Dict[str, str] = decode(
                ticket,
                self.__jwt_key,
                [self.__jwt_algorithm]
            )
        except InvalidTokenError or DecodeError or InvalidSignatureError or ExpiredSignatureError:
            raise InvalidAccessTokenError("Provided ticket is invalid or expired")

        if "id" not in ticket or "mode" not in ticket:
            raise InvalidAccessTokenError("Provided ticket is invalid")

        if ticket.get("mode") != "ticket":
            raise InvalidAccessTokenError("Provided ticket is invalid")

        return ticket

    async def verify_access_token(
            self,
            access_token: str,
            *,
            users_controller: UsersController
    ) -> User:
        data: Dict[str, str] = await asyncio.to_thread(self.decode_access_token, access_token)

        try:
            user_id: UUID = UUID(data["id"])
        except ValueError:
            raise InvalidCredentialsError("Provided access credentials are invalid")

        user: User | None = await users_controller.get_user(user_id)

        if user is None:
            raise InvalidCredentialsError("Provided access credentials are invalid")

        return user  # TODO: Add password check

    @staticmethod
    def dependency(config: Annotated[Config, Depends(Dependency.config)]) -> 'Authenticator':
        return Authenticator(
            jwt_key=config.jwt_key.get_secret_value(),
            jwt_algorithm=config.jwt_algorithm
        )

    @staticmethod
    def websocket_dependency(config: Annotated[Config, Depends(Dependency.config_websocket)]) -> 'Authenticator':
        return Authenticator(
            jwt_key=config.jwt_key.get_secret_value(),
            jwt_algorithm=config.jwt_algorithm
        )

    @staticmethod
    def verify_access_token_dependency() -> Depends:
        async def __verify_access_token(
                access_token: Annotated[str, Header()],
                authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)],
                users_controller: Annotated[UsersController, Depends(UsersController.dependency)],
        ) -> None:
            await authenticator.verify_access_token(access_token, users_controller=users_controller)

        return Depends(__verify_access_token)

    @staticmethod
    def get_user() -> Depends:
        async def __get_user(
                access_token: Annotated[str, Header()],
                authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)],
                users_controller: Annotated[UsersController, Depends(UsersController.dependency)],
        ) -> User:
            return await authenticator.verify_access_token(access_token, users_controller=users_controller)

        return Depends(__get_user)

    @staticmethod
    def authenticate_websocket_dependency() -> Depends:
        async def __authenticate_websocket(
                websocket: WebSocket,
                authenticator: Annotated[Authenticator, Depends(Authenticator.websocket_dependency)],
                connections: Annotated[ConnectionsController, Depends(ConnectionsController.websocket_dependency)],
                users_controller: Annotated[UsersController, Depends(UsersController.websocket_dependency)]
        ) -> None:
            await websocket.accept()

            try:
                auth_packet: ClientAuthPacket = ClientAuthPacket.unpack(await websocket.receive_text())
            except InvalidPacketError:
                await websocket.close(3000, "Provided authorization packet data is invalid")
                return

            try:
                ticket: Dict[str, str] = await asyncio.to_thread(
                    authenticator.decode_ticket,
                    auth_packet.ticket
                )
            except InvalidAccessTokenError:
                await websocket.close(3000, "Provided authorization ticket is invalid")
                return

            try:
                user_id: UUID = UUID(ticket["id"])
            except ValueError:
                await websocket.close(3000, "Provided authorization ticket is invalid")
                return

            user: User | None = await users_controller.get_user(user_id)

            if user is None:
                await websocket.close(3000, "Provided authorization ticket is invalid")
                return

            await connections.add_connection(websocket, user.user_id)

            auth_response_packet: ServerAuthPacket = ServerAuthPacket(
                user.user_id,
                user.username
            )

            await websocket.send_text(auth_response_packet.pack())

        return Depends(__authenticate_websocket)

    @staticmethod
    def get_websocket_user() -> Depends:
        async def __get_websocket_user(
                websocket: WebSocket,
                connections: Annotated[ConnectionsController, Depends(ConnectionsController.websocket_dependency)],
                users_controller: Annotated[UsersController, Depends(UsersController.websocket_dependency)],
        ) -> User:
            user: User | None = await users_controller.get_user(await connections.get_user_id(websocket))

            if user is None:
                raise NotAuthenticatedAddressError("Provided websocket address is not authenticated")

            return user

        return Depends(__get_websocket_user)
