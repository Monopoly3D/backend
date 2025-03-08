from dataclasses import field as dataclass_field
from typing import Dict, Any, Set

from pydantic.dataclasses import dataclass

from app.assets.objects.game_object import GameObject


@dataclass
class Monopoly(GameObject):
    fields: Set[int] = dataclass_field(default_factory=set)
    is_filiated: bool = False

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return Monopoly(**data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "fields": self.fields,
            "is_filiated": self.is_filiated
        }

    def add(
            self,
            field: int
    ) -> None:
        self.fields.add(field)
