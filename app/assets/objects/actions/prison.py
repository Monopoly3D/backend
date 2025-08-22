from pydantic.dataclasses import dataclass

from app.assets.objects.actions.abstract import AbstractAction
from app.assets.enums.action_type import ActionType


@dataclass
class PrisonAction(AbstractAction):
    ACTION_TYPE = ActionType.PRISON
