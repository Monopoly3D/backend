from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.assets.actions.action import Action
from app.assets.enums.action_type import ActionType


@dataclass
class BuyFieldAction(Action):
    ACTION_TYPE = ActionType.BUY_FIELD

    cost: int

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Action':
        return cls(cost=data.get("cost"))

    def to_json(self) -> Dict[str, Any]:
        return {"cost": self.cost}
