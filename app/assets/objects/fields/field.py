from typing import Dict, Any

from app.assets.enums.field_type import FieldType
from app.assets.objects.monopoly_object import MonopolyObject


class Field(MonopolyObject):
    def __init__(
            self,
            field_id: int,
            *,
            field_type: FieldType
    ) -> None:
        self.field_id = field_id
        self.field_type = field_type

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.field_id,
            "type": self.field_type.value
        }
