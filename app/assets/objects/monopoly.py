from dataclasses import field as dataclass_field
from typing import Dict, Any, List

from pydantic.dataclasses import dataclass

from app.assets.objects.fields.company import Company
from app.assets.objects.game_object import GameObject


@dataclass
class Monopoly(GameObject):
    companies: List[Company] = dataclass_field(default_factory=list)
    is_filiated: bool = False

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "is_filiated": self.is_filiated
        }

    @property
    def is_monopoly(self) -> bool:
        if not len(self.companies) or self.companies[0].owner_id is None:
            return False

        return len(set(company.owner_id for company in self.companies)) == 1

    @is_monopoly.setter
    def is_monopoly(self, value: bool) -> None:
        for company in self.companies:
            company.is_monopoly = value

    @property
    def highest_filiation(self) -> int:
        return max(company.filiation for company in self.companies)

    @property
    def lowest_filiation(self) -> int:
        return min(company.filiation for company in self.companies)
