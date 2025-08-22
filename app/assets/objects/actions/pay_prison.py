from pydantic.dataclasses import dataclass

from app.assets.enums.action_type import ActionType
from app.assets.objects.actions.abstract import AbstractAction


@dataclass
class PayPrisonAction(AbstractAction):
    ACTION_TYPE = ActionType.PAY_PRISON
