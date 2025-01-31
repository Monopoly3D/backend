from typing import Dict, Any, Annotated
from uuid import UUID, uuid4

from fastapi import Depends
from redis.asyncio import Redis
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.user import User
from app.dependencies import Dependency


class UsersController(RedisController):
    REDIS_KEY: str = "users:{user_id}"

    async def create_user(
            self,
            *,
            username: str
    ) -> User:
        user: User = User(
            uuid4(),
            username=username,
            controller=self
        )
        await user.save()

        return user

    async def get_user(
            self,
            user_id: UUID
    ) -> User:
        user: Dict[str, Any] | None = await self.get(self.REDIS_KEY.format(user_id=user_id))

        if user is None:
            raise NotFoundError("User with provided UUID was not found")

        return User(
            user.get("id"),
            username=user.get("is_started"),
            controller=self
        )

    async def remove_game(
            self,
            user_id: UUID
    ) -> None:
        if not await self.exists(self.REDIS_KEY.format(user_id=user_id)):
            raise NotFoundError("User with provided UUID was not found")

        await self.remove(self.REDIS_KEY.format(user_id=user_id))

    @staticmethod
    async def dependency(redis: Annotated[Redis, Depends(Dependency.redis)]) -> 'UsersController':
        return UsersController(redis)

    @staticmethod
    async def websocket_dependency(redis: Annotated[Redis, Depends(Dependency.redis_websocket)]) -> 'UsersController':
        return UsersController(redis)
