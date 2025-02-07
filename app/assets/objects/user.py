from typing import Any, Dict
from uuid import UUID

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.api.v1.controllers.redis import RedisController
from app.assets.objects.redis import RedisObject


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class User(RedisObject):
    user_id: UUID
    username: str

    __controller: RedisController | None = None

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "user_id": str(self.user_id),
            "username": self.username
        }

    @property
    def controller(self) -> None:
        return self.__controller

    @controller.setter
    def controller(self, value: Any) -> None:
        super().__init__(value.REDIS_KEY.format(user_id=self.user_id), value)
        self.__controller = value
