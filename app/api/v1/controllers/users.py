from typing import Dict, Any
from uuid import UUID, uuid4

from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.user import User


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
        user: Dict[str, Any] | None = await self.get(self.REDIS_KEY.format(user_id))

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
        if not await self.exists(self.REDIS_KEY.format(user_id)):
            raise NotFoundError("User with provided UUID was not found")

        await self.remove(self.REDIS_KEY.format(user_id))
