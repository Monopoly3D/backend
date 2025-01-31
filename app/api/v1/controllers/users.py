from typing import Dict, Any, Annotated
from uuid import UUID, uuid4

from fastapi import Depends
from redis import Redis

from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.user import User
from app.dependencies import Dependency


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

    @staticmethod
    def dependency() -> Depends:
        async def __dependency(redis: Annotated[Redis, Depends(Dependency.redis)]) -> UsersController:
            return UsersController(redis)

        return Depends(__dependency)
