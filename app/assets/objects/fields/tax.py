from typing import Any, Dict

from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field
from app.assets.objects.player import Player


@dataclass
class Tax(Field):
    FIELD_TYPE = FieldType.TAX

    tax_amount: int = 0

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        if "tax" not in data:
            return

        return cls(
            data.get("id"),
            **data.get("tax")
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.field_id,
            "type": self.FIELD_TYPE.value,
            "tax": {
                "tax_amount": self.tax_amount
            }
        }

    async def on_stand(
            self,
            player: Player
    ) -> None:
        pass
