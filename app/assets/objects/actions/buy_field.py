from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.assets.enums.action_type import ActionType
from app.assets.objects.actions.abstract import AbstractAction


@dataclass
class BuyFieldAction(AbstractAction):
    ACTION_TYPE = ActionType.BUY_FIELD

    cost: int

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'AbstractAction':
        return cls(cost=data.get("cost"))

    def to_json(self) -> Dict[str, Any]:
        return {"cost": self.cost}
