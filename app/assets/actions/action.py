from abc import ABC
from typing import Dict, Any, ClassVar

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.assets.enums.action_type import ActionType


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Action(ABC):
    ACTION_TYPE: ClassVar[ActionType]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Action':
        return cls()

    def to_json(self) -> Dict[str, Any]:
        return {}

    @classmethod
    def unpack(cls, data: Dict[str, Any]) -> 'Action':
        return cls.from_json(data)

    def pack(self) -> Dict[str, Any]:
        return {"action_type": self.ACTION_TYPE.value, **self.to_json()}
