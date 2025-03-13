from pydantic.dataclasses import dataclass

from app.assets.actions.action import Action
from app.assets.enums.action_type import ActionType


@dataclass
class MoveAction(Action):
    ACTION_TYPE = ActionType.MOVE
