from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.assets.objects.actions.abstract import AbstractAction
from app.assets.enums.action_type import ActionType


@dataclass
class PayTaxAction(AbstractAction):
    ACTION_TYPE = ActionType.PAY_TAX

    amount: int

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(amount=data.get("amount"))

    def to_json(self) -> Dict[str, Any]:
        return {"amount": self.amount}
