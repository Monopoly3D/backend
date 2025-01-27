from typing import Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.assets.base.monopoly_object import MonopolyObject
from app.assets.base.redis_object import RedisObject


class Game(MonopolyObject, RedisObject, BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    uuid: UUID
    is_started: bool = False

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Game':
        return cls(
            uuid=UUID(data.get("uuid")),
            is_started=data.get("is_started")
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "uuid": str(self.uuid),
            "is_started": self.is_started
        }

    def to_recruitment(self) -> Dict[str, Any]:
        return {
            "uuid": str(self.uuid)
        }
