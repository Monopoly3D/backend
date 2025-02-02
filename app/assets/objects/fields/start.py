from typing import Dict, Any

from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field


class Start(Field):
    FIELD_TYPE = FieldType.START

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls(data.get("id"))
