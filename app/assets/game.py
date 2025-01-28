from typing import Any, Dict
from uuid import UUID

from app.api.v1.controllers.redis import RedisController
from app.assets.monopoly_object import MonopolyObject
from app.assets.redis_object import RedisObject


class Game(MonopolyObject, RedisObject):
    def __init__(
            self,
            uuid: UUID,
            *,
            is_started: bool = False,
            controller: RedisController
    ) -> None:
        self.uuid = uuid
        self.is_started = is_started

        self.__controller = controller

    async def save(self) -> None:
        await self.__controller.create(f"games:{self.uuid}", self.to_json())

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": str(self.uuid),
            "is_started": self.is_started
        }
