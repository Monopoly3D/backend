from typing import Dict, Any
from uuid import UUID, uuid4

from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.user import User


class UsersController(RedisController):
    async def create_user(
            self,
            *,
            username: str
    ) -> User:
        user: User = User(
            uuid4(),
            username=username,
            controller=super()
        )
        await user.save()

        return user

    async def get_user(
            self,
            uuid: UUID
    ) -> User:
        user: Dict[str, Any] | None = await self.get(f"users:{uuid}")

        if user is None:
            raise NotFoundError("User with provided UUID was not found")

        return User(
            user.get("id"),
            username=user.get("is_started"),
            controller=self
        )

    async def remove_game(
            self,
            uuid: UUID
    ) -> None:
        if not await self.exists(f"users:{uuid}"):
            raise NotFoundError("User with provided UUID was not found")

        await self.remove(f"users:{uuid}")
