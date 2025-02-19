from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.assets.actions.action import Action
from app.assets.enums.action_type import ActionType


@dataclass
class MoveAction(Action):
    action_type: ActionType = ActionType.MOVE

    player: int = 0

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(player=data.get("player"))

    def to_json(self) -> Dict[str, Any]:
        return {"action_type": self.action_type.value,"player": self.player}

