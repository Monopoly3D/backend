from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field
from app.assets.objects.player import Player


@dataclass
class Casino(Field):
    field_type = FieldType.CASINO

    async def on_stand(
            self,
            player: Player
    ) -> None:
        pass
