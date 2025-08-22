from typing import Any

from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.abstract import AbstractField


@dataclass
class Prison(AbstractField):
    FIELD_TYPE = FieldType.PRISON

    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        await self.game.next()
