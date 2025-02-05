from typing import Dict, Any, Annotated, Tuple
from uuid import UUID, uuid4

from fastapi import Depends
from redis.asyncio import Redis

from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.http.not_found import NotFoundError
from app.assets.objects.user import User
from app.dependencies import Dependency


class UsersController(RedisController):
    REDIS_KEY: str = "users:{user_id}"

    async def create_user(
            self,
            *,
            username: str
    ) -> User:
        user = User(uuid4(), username)
        user.controller = self
        await user.save()

        return user

    async def get_user(
            self,
            user_id: UUID
    ) -> User | None:
        user: Dict[str, Any] | None = await self.get(self.REDIS_KEY.format(user_id=user_id))

        if user is None:
            return

        user: User = User.from_json(user)
        user.controller = self
        return user

    async def get_user_by_username(
            self,
            username: str
    ) -> User | None:
        users: Tuple[str, ...] = await self.get_keys(pattern="users")

        for user_key in users:
            user: Dict[str, Any] = await self.get(user_key, exact_key=True)

            if user is not None and user.get("username") == username:
                user: User = User.from_json(user)
                user.controller = self
                return user

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
