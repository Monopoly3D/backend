from abc import ABC
from typing import Dict, Any

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.assets.enums.action_type import ActionType


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Action(ABC):
    action_type: ActionType

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return {"action_type": self.action_type.value}
