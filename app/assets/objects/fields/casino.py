from typing import Dict, Any

from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field
from app.assets.objects.player import Player


class Casino(Field):
    FIELD_TYPE = FieldType.CASINO

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls(data.get("id"))

    async def on_stand(
            self,
            player: Player,
            amount: int
    ) -> None:
        pass
