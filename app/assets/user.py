from uuid import UUID

from app.api.v1.controllers.redis import RedisController
from app.assets.monopoly_object import MonopolyObject
from app.assets.redis_object import RedisObject


class User(MonopolyObject, RedisObject):
    def __init__(
            self,
            uuid: UUID,
            *,
            username: str,
            controller: RedisController
    ) -> None:
        self.uuid = uuid
        self.username = username

        self.__controller = controller

    async def save(self) -> None:
        await self.__controller.create(
            f"users:{self.uuid}",
            {
                "id": str(self.uuid),
                "username": self.username
            }
        )
