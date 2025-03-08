from abc import ABC, abstractmethod
from typing import Dict, Any

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.assets.enums.action_type import ActionType


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Action(ABC):
    action_type: ActionType

    @classmethod
    @abstractmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Action':
        pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass

    @classmethod
    def unpack(
            cls,
            data: Dict[str, Any]
    ) -> 'Action':
        return cls.from_json(data)

    def pack(self) -> Dict[str, Any]:
        return {"action_type": self.action_type.value, **self.to_json()}
