from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.assets.objects.fields.company import Company


class CompanyResponseModel(BaseModel):
    owner_id: UUID | None = None
    is_monopoly: bool
    field_dependant: bool
    dice_dependant: bool
    rent: List[int]
    mortgage: int
    filiation: int
    cost: int
    mortgage_cost: int
    buyout_cost: int
    filiation_cost: int

    @classmethod
    def from_company(
            cls,
            company: Company
    ) -> 'CompanyResponseModel':
        return cls(
            owner_id=company.owner_id,
            is_monopoly=company.is_monopoly,
            field_dependant=company.field_dependant,
            dice_dependant=company.dice_dependant,
            rent=company.rent,
            mortgage=company.mortgage,
            filiation=company.filiation,
            cost=company.cost,
            mortgage_cost=company.mortgage_cost,
            buyout_cost=company.buyout_cost,
            filiation_cost=company.filiation_cost
        )
