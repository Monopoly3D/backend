from typing import Any

from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


@dataclass
class Chance(Field):
    FIELD_TYPE = FieldType.CHANCE

    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        await self.game.next()
