from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.assets.actions.action import Action
from app.assets.enums.action_type import ActionType


@dataclass
class PayChanceAction(Action):
    ACTION_TYPE = ActionType.PAY_CHANCE

    amount: int

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(amount=data.get("amount"))

    def to_json(self) -> Dict[str, Any]:
        return {"amount": self.amount}
