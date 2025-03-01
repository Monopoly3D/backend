from typing import Any

from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


@dataclass
class Prison(Field):
    field_type: FieldType = FieldType.PRISON

    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        await self.game.next()
