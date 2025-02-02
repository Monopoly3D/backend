from typing import Dict, Any

from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field


class Casino(Field):
    FIELD_TYPE = FieldType.CASINO

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls(data.get("id"))
