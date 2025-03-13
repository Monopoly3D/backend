from dataclasses import field as dataclass_field
from typing import Dict, Any, Set, List

from pydantic.dataclasses import dataclass

from app.assets.objects.fields.company import Company
from app.assets.objects.game_object import GameObject


@dataclass
class Monopoly(GameObject):
    fields: Set[Company] = dataclass_field(default_factory=set)
    is_filiated: bool = False

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        data_fields: List[Dict[str, Any]] = data.pop("fields")

        fields: Set[Company] = set()

        if data_fields is not None:
            for field in data_fields:
                fields.add(Company.from_json(field))

        return cls(fields=fields, **data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "fields": [field.to_json() for field in self.fields],
            "is_filiated": self.is_filiated
        }

    def add(
            self,
            field: Company
    ) -> None:
        self.fields.add(field)
