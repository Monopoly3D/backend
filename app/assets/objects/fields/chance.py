from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field
from app.assets.objects.player import Player


@dataclass
class Chance(Field):
    field_type: FieldType = FieldType.CHANCE

    async def on_stand(
            self,
            player: Player
    ) -> None:
        pass
