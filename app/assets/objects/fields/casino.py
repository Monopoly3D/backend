from typing import Any

from pydantic.dataclasses import dataclass

from app.assets.actions.casino import CasinoAction
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


@dataclass
class Casino(Field):
    field_type: FieldType = FieldType.CASINO

    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        self.game.action = CasinoAction()
