from pydantic.dataclasses import dataclass

from app.assets.actions.action import Action
from app.assets.enums.action_type import ActionType


@dataclass
class PayPrisonAction(Action):
    ACTION_TYPE = ActionType.PAY_PRISON
