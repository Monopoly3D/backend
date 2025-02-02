from typing import Dict, Any

from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field


class Police(Field):
    FIELD_TYPE = FieldType.POLICE

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls(data.get("id"))
