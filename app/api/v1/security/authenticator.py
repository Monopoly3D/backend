from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from jwt import encode
from pytz import utc

from app.dependencies import Dependency
from config import Config


class Authenticator:
    ACCESS_TOKEN_EXPIRE = 15

    def __init__(
            self,
            jwt_key: str,
            jwt_algorithm: str
    ) -> None:
        self.__jwt_key = jwt_key
        self.__jwt_algorithm = jwt_algorithm

    def create_access_token(
            self,
            *,
            user_id: UUID,
            username: str
    ) -> str:
        return encode(
            {
                "id": str(user_id),
                "username": username,
                "exp": datetime.now(utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE),
                "mode": "access"
            },
            self.__jwt_key,
            self.__jwt_algorithm
        )

    @classmethod
    async def dependency(
            cls,
            config: Annotated[Config, Depends(Dependency.config)]
    ) -> 'Authenticator':
        return cls(config.jwt_key.get_secret_value(), config.jwt_algorithm)
