from typing import Dict, Any

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


class Police(Field):
    def __init__(
            self,
            field_id: int
    ) -> None:
        super().__init__(field_id, field_type=FieldType.POLICE)

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        if "id" not in data:
            return

        return cls(data.get("id"))
