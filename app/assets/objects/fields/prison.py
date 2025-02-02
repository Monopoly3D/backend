from typing import Dict, Any

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


class Prison(Field):
    def __init__(
            self,
            field_id: int
    ) -> None:
        super().__init__(field_id, field_type=FieldType.PRISON)

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        if "id" not in data:
            return

        return cls(data.get("id"))
