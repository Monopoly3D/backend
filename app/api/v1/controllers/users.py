import asyncio
from typing import Dict, Any, Tuple
from uuid import UUID, uuid4

from redis import Redis

from app.api.v1.controllers.redis import RedisController
from app.assets.objects.user import User


class UsersController(RedisController):
    REDIS_KEY: str = "users:{user_id}"

    def __init__(
            self,
            redis: Redis
    ) -> None:
        super().__init__(redis)
        self.users: Dict[UUID, User] = {}

    async def create_user(
            self,
            *,
            username: str
    ) -> User:
        user = User(uuid4(), username)
        user.controller = self

        self.users[user.user_id] = user
        await user.save()

        return user

    async def get_user(
            self,
            user_id: UUID
    ) -> User | None:
        user: User | None = self.users.get(user_id)

        if user is None:
            user: Dict[str, Any] | None = await self.get(self.REDIS_KEY.format(user_id=user_id))
            if user is None:
                return
            user: User = User.from_json(user)
            self.users[user.user_id] = user

        user.controller = self
        return user

    async def get_users(self) -> Tuple[User]:
        user_uuids: Tuple[str, ...] = await self.get_keys(pattern="users")

        users: Tuple[Any] = await asyncio.gather(
            *[self.get_user(UUID(user.split(":")[-1])) for user in user_uuids]
        )

        return tuple(filter(lambda user: isinstance(user, User), users))

    async def get_user_by_username(
            self,
            username: str
    ) -> User | None:
        user: User | None = [user for user in self.users.values() if user.username == username][0]

        if user is not None:
            return user

        users: Tuple[str, ...] = await self.get_keys(pattern="users")

        for user_key in users:
            user: Dict[str, Any] = await self.get(user_key, exact_key=True)

            if user is not None and user.get("username") == username:
                user: User = User.from_json(user)
                self.users[user.user_id] = user

                user.controller = self
                return user

    async def retrieve_users(self) -> None:
        self.users.update({user.user_id: user for user in await self.get_users()})
