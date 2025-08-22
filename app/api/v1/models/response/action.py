from pydantic import BaseModel, ConfigDict

from app.assets.enums.action_type import ActionType
from app.assets.objects.actions.abstract import AbstractAction


class ActionResponseModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    action_type: ActionType

    @classmethod
    def from_action(
            cls,
            action: AbstractAction | None
    ) -> 'ActionResponseModel':
        return cls(**action.pack()) if action is not None else None
