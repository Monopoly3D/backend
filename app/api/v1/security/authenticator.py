import asyncio
from datetime import datetime, timedelta
from typing import Dict, Annotated
from uuid import UUID

from fastapi import Depends, Header
from jwt import encode, decode, InvalidTokenError
from pytz import utc

from app.api.v1.controllers.users import UsersController
from app.api.v1.exceptions.invalid_access_token_error import InvalidAccessTokenError
from app.api.v1.exceptions.invalid_credentials_error import InvalidCredentialsError
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.user import User
from app.dependencies import Dependency
from config import Config


class Authenticator:
    ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
    TICKET_EXPIRE = timedelta(seconds=60)

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

    def decode_access_token(
            self,
            access_token: str
    ) -> Dict[str, str]:
        try:
            return decode(
                access_token,
                self.__jwt_key,
                [self.__jwt_algorithm]
            )
        except InvalidTokenError:
            raise InvalidAccessTokenError("Provided access token is invalid or expired")

    async def verify_access_token(
            self,
            access_token: str,
            *,
            users_controller: UsersController
    ) -> None:
        data: Dict[str, str] = await asyncio.to_thread(self.decode_access_token, access_token)

        if data.get("mode") != "access":
            raise InvalidAccessTokenError("Provided access token is invalid")

        try:
            user: User = await users_controller.get_user(UUID(data.get("id")))
        except NotFoundError or ValueError:
            raise InvalidCredentialsError("Provided access credentials are invalid")

        print(user.username)  # TODO: Add password check

    @staticmethod
    def dependency(config: Annotated[Config, Depends(Dependency.config)]) -> 'Authenticator':
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
