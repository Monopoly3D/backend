import asyncio
from datetime import datetime, timedelta
from typing import Dict, Annotated, List, Any
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, Form
from fastapi.security import OAuth2PasswordBearer
from jwt import encode, decode, InvalidTokenError
from pytz import utc
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.responses import Response
from starlette.websockets import WebSocket

from app.api.v1.exceptions.http.invalid_access_token import InvalidAccessTokenError
from app.api.v1.exceptions.http.invalid_credentials import InvalidCredentialsError
from app.api.v1.exceptions.websocket.not_authenticated_address import NotAuthenticatedAddressError
from app.assets.controllers.connections import ConnectionsController
from app.database.models import User, Role, UserRefreshToken
from app.dependencies import config_websocket, config_dependency, database_session, database_websocket_session
from config import Config


class Authenticator:
    ACCESS_TOKEN_EXPIRE = timedelta(weeks=100)
    REFRESH_TOKEN_EXPIRE = timedelta(weeks=100)
    REGISTER_TOKEN_EXPIRE = timedelta(weeks=100)
    TICKET_EXPIRE = timedelta(weeks=100)

    OAUTH_SCHEME: OAuth2PasswordBearer = OAuth2PasswordBearer("/api/v1/auth")

    def __init__(
            self,
            *,
            jwt_key: str,
            jwt_algorithm: str
    ) -> None:
        self.__jwt_key = jwt_key
        self.__jwt_algorithm = jwt_algorithm
        self.__ph = PasswordHasher()

    async def hash(
            self,
            string: str
    ) -> str:
        return await asyncio.to_thread(self.__ph.hash, string)

    async def verify(
            self,
            string: str,
            string_hash: str
    ) -> bool:
        try:
            await asyncio.to_thread(self.__ph.verify, string_hash, string)
            return True
        except VerifyMismatchError:
            return False

    async def create_access_token(
            self,
            user_id: UUID
    ) -> str:
        return await asyncio.to_thread(
            encode,
            {
                "id": str(user_id),
                "exp": datetime.now(utc) + self.ACCESS_TOKEN_EXPIRE,
                "mode": "access"
            },
            self.__jwt_key,
            self.__jwt_algorithm
        )

    async def create_refresh_token(
            self,
            user_id: UUID
    ) -> str:
        return await asyncio.to_thread(
            encode,
            {
                "id": str(user_id),
                "exp": datetime.now(utc) + self.REFRESH_TOKEN_EXPIRE,
                "mode": "refresh"
            },
            self.__jwt_key,
            self.__jwt_algorithm
        )

    async def create_new_refresh_token(
            self,
            user_id: UUID,
            session: AsyncSession
    ) -> str:
        refresh_token: str = await self.create_refresh_token(user_id)
        hashed_refresh_token: str = await self.hash(refresh_token)

        user_refresh_token: UserRefreshToken | None = await session.scalar(
            select(UserRefreshToken)
            .filter_by(user_id=user_id)
        )

        if user_refresh_token is None:
            session.add(
                UserRefreshToken(
                    user_id=user_id,
                    refresh_token=hashed_refresh_token
                )
            )
        else:
            await session.execute(
                update(UserRefreshToken)
                .filter_by(user_id=user_id)
                .values(refresh_token=hashed_refresh_token)
            )

        return refresh_token

    @staticmethod
    def set_refresh_token_cookie(
            response: Response,
            refresh_token: str
    ) -> None:
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=True,
            samesite="none"
        )

    async def create_register_token(
            self,
            username: str,
            email: str,
            password_hash: str
    ) -> str:
        return await asyncio.to_thread(
            encode,
            {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "exp": datetime.now(utc) + self.REFRESH_TOKEN_EXPIRE,
                "mode": "register"
            },
            self.__jwt_key,
            self.__jwt_algorithm
        )

    async def create_game_ticket(
            self,
            game_id: UUID,
            user_id: UUID
    ) -> str:
        return await asyncio.to_thread(
            encode,
            {
                "id": str(user_id),
                "game_id": str(game_id),
                "exp": datetime.now(utc) + self.TICKET_EXPIRE,
                "mode": "game_ticket"
            },
            self.__jwt_key,
            self.__jwt_algorithm
        )

    async def decode_access_token(
            self,
            access_token: str
    ) -> Dict[str, str]:
        return await self.__decode_token(access_token, "access")

    async def decode_refresh_token(
            self,
            refresh_token: str
    ) -> Dict[str, str]:
        return await self.__decode_token(refresh_token, "refresh")

    async def decode_register_token(
            self,
            register_token: str
    ) -> Dict[str, Any]:
        return await self.__decode_token(register_token, "register")

    async def decode_game_ticket(
            self,
            ticket: str
    ) -> Dict[str, str]:
        return await self.__decode_token(ticket, "game_ticket")

    async def verify_access_token(
            self,
            access_token: str,
            session: AsyncSession
    ) -> User:
        return await self.__verify_token(access_token, "access", session)

    async def verify_refresh_token(
            self,
            refresh_token: str,
            session: AsyncSession
    ) -> User:
        data: Dict[str, str] = await self.__decode_token(refresh_token, "refresh")

        try:
            user_id: UUID = UUID(data["id"])
        except ValueError:
            raise InvalidCredentialsError("Provided credentials are invalid")

        user: User | None = await session.scalar(
            select(User)
            .filter_by(id=user_id)
            .options(
                joinedload(User.roles),
                joinedload(User.refresh_token)
            )
        )

        if user is None:
            raise InvalidCredentialsError("Provided credentials are invalid")

        return user

    async def __decode_token(
            self,
            token: str,
            mode: str
    ) -> Dict[str, str]:
        try:
            token: Dict[str, str] = await asyncio.to_thread(
                decode,
                token,
                self.__jwt_key,
                [self.__jwt_algorithm]
            )
        except InvalidTokenError:
            raise InvalidAccessTokenError("Provided token is invalid or expired")

        if "mode" not in token:
            raise InvalidAccessTokenError("Provided token is invalid")

        if token.get("mode") != mode:
            raise InvalidAccessTokenError("Provided token is invalid")

        return token

    async def __verify_token(
            self,
            token: str,
            mode: str,
            session: AsyncSession
    ) -> User:
        data: Dict[str, str] = await self.__decode_token(token, mode)

        try:
            user_id: UUID = UUID(data["id"])
        except ValueError:
            raise InvalidCredentialsError("Provided credentials are invalid")

        user: User | None = await session.scalar(
            select(User)
            .filter_by(id=user_id)
            .options(joinedload(User.roles))
        )

        if user is None:
            raise InvalidCredentialsError("Provided credentials are invalid")

        return user

    @staticmethod
    def dependency(config: Annotated[Config, Depends(config_dependency)]) -> 'Authenticator':
        return Authenticator(
            jwt_key=config.jwt_key.get_secret_value(),
            jwt_algorithm=config.jwt_algorithm
        )

    @staticmethod
    def websocket_dependency(config: Annotated[Config, Depends(config_websocket)]) -> 'Authenticator':
        return Authenticator(
            jwt_key=config.jwt_key.get_secret_value(),
            jwt_algorithm=config.jwt_algorithm
        )

    @classmethod
    def get_register_user(cls) -> Depends:
        async def __get_register_user(
                register_token: Annotated[str, Form()],
                authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
        ) -> User:
            credentials: Dict[str, str] = await authenticator.decode_register_token(register_token)

            return User(
                username=credentials.get("username"),
                email=credentials.get("email"),
                password_hash=credentials.get("password_hash")
            )

        return Depends(__get_register_user)

    @classmethod
    def get_user(cls) -> Depends:
        async def __get_user(
                access_token: Annotated[str, Depends(cls.OAUTH_SCHEME)],
                session: Annotated[AsyncSession, Depends(database_session)],
                authenticator: Annotated[Authenticator, Depends(Authenticator.dependency)]
        ) -> User:
            return await authenticator.verify_access_token(access_token, session)

        return Depends(__get_user)

    @classmethod
    def get_roles(cls) -> Depends:
        async def __get_roles(user: Annotated[User, cls.get_user()]) -> List[Role]:
            return [Role(role.role) for role in user.roles]

        return Depends(__get_roles)

    @staticmethod
    def get_websocket_user() -> Depends:
        async def __get_websocket_user(
                websocket: WebSocket,
                session: Annotated[AsyncSession, Depends(database_websocket_session)],
                connections: Annotated[ConnectionsController, Depends(ConnectionsController.websocket_dependency)]
        ) -> User:
            user: User | None = await session.scalar(
                select(User)
                .filter_by(id=await connections.get_user_id(websocket))
                .options(joinedload(User.roles))
            )

            if user is None:
                raise NotAuthenticatedAddressError("Provided websocket address is not authenticated")

            return user

        return Depends(__get_websocket_user)
