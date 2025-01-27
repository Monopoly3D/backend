from typing import Dict, Any
from uuid import UUID, uuid4

from app.assets.base.monopoly_object import MonopolyObject
from app.assets.base.redis_object import RedisObject


class Game(MonopolyObject, RedisObject):
    def __init__(
            self,
            *,
            uuid: UUID | None = None,
            is_started: bool = False
    ) -> None:
        self.uuid: UUID = uuid or uuid4()
        self.is_started = is_started

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
