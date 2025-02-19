from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.assets.actions.action import Action
from app.assets.enums.action_type import ActionType


@dataclass
class BuyField(Action):
    action_type: ActionType = ActionType.BUY_FIELD

    cost: int = 0

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(cost=data.get("cost"))

    def to_json(self) -> Dict[str, Any]:
        return {"action_type": self.action_type.value,"cost": self.cost}
