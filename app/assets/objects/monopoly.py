from dataclasses import field as dataclass_field
from typing import Dict, Any, List

from pydantic.dataclasses import dataclass

from app.assets.objects.fields.company import Company
from app.assets.objects.game_object import GameObject


@dataclass
class Monopoly(GameObject):
    companies: List[Company] = dataclass_field(default_factory=set)
    is_filiated: bool = False

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        data_companies: List[Dict[str, Any]] = data.pop("fields")

        companies: List[Company] = list()

        if data_companies is not None:
            for company in data_companies:
                companies.append(Company.from_json(company))

        return cls(companies=companies, **data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "companies": [company.to_json() for company in self.companies],
            "is_filiated": self.is_filiated
        }

    def add(
            self,
            company: Company
    ) -> None:
        company.monopoly = self
        self.companies.append(company)

    @property
    def is_monopoly(self) -> bool:
        if not len(self.companies) or self.companies[0].owner_id is None:
            return False

        return len(set(company.owner_id for company in self.companies)) == 1

    @is_monopoly.setter
    def is_monopoly(self, value: bool) -> None:
        for company in self.companies:
            company.is_monopoly = value
