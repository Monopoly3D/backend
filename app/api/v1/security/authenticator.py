import asyncio
from datetime import datetime, timedelta
from typing import Dict, Annotated
from uuid import UUID

from fastapi import Depends, Header
from jwt import encode, decode, InvalidTokenError, DecodeError, ExpiredSignatureError, InvalidSignatureError
from pytz import utc

from app.api.v1.controllers.users import UsersController
from app.api.v1.exceptions.invalid_access_token_error import InvalidAccessTokenError
from app.api.v1.exceptions.invalid_credentials_error import InvalidCredentialsError
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.redis.user import User
from app.dependencies import Dependency
from config import Config


class Authenticator:
    ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
    TICKET_EXPIRE = timedelta(seconds=1)

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
            user: User = await users_controller.get_user(UUID(data["id"]))
        except NotFoundError or ValueError:
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
