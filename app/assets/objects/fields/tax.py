from typing import Any, Dict

from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field
from app.assets.objects.player import Player


class Tax(Field):
    FIELD_TYPE = FieldType.TAX

    def __init__(
            self,
            field_id: int,
            *,
            tax_amount: int
    ) -> None:
        super().__init__(field_id)

        self.tax_amount = tax_amount

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        if "tax" not in data:
            return

        tax: Dict[str, Any] = data["tax"]

        return cls(
            data.get("id"),
            tax_amount=tax.get("tax_amount")
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
