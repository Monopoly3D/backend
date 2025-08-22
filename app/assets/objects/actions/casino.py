from pydantic.dataclasses import dataclass

from app.assets.enums.action_type import ActionType
from app.assets.objects.actions.abstract import AbstractAction


@dataclass
class CasinoAction(AbstractAction):
    ACTION_TYPE = ActionType.CASINO
