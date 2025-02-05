from typing import Dict, Any

from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field
from app.assets.objects.player import Player


@dataclass
class Chance(Field):
    FIELD_TYPE = FieldType.CHANCE

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls(**data)

    async def on_stand(
            self,
            player: Player
    ) -> None:
        pass
