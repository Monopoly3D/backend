from abc import ABC
from typing import Dict, Any, ClassVar

from pydantic.dataclasses import dataclass

from app.assets.enums.action_type import ActionType
from app.assets.objects.object import GameObject


@dataclass
class AbstractAction(GameObject, ABC):
    ACTION_TYPE: ClassVar[ActionType]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'AbstractAction':
        return cls()

    def to_json(self) -> Dict[str, Any]:
        return {}

    @classmethod
    def unpack(cls, data: Dict[str, Any]) -> 'AbstractAction':
        return cls.from_json(data)

    def pack(self) -> Dict[str, Any]:
        return {"action_type": self.ACTION_TYPE.value, **self.to_json()}
