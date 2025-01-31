from typing import Any, Dict

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


class Tax(Field):
    def __init__(
            self,
            field_id: int,
            *,
            tax_amount: int
    ) -> None:
        super().__init__(field_id, field_type=FieldType.COMPANY)

        self.tax_amount = tax_amount

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.field_id,
            "type": self.field_type.value,
            "tax": {
                "tax_amount": self.tax_amount
            }
        }
