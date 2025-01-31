from typing import List, Any, Dict
from uuid import UUID

from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


class Company(Field):
    def __init__(
            self,
            field_id: int,
            *,
            owner_id: UUID | None = None,
            is_monopoly: bool = False,
            field_dependant: bool = False,
            dice_dependant: bool = False,
            rent: List[int],
            mortgage: int,
            filiation: int,
            cost: int,
            mortgage_cost: int,
            buyout_cost: int,
            filiation_cost: int
    ) -> None:
        super().__init__(field_id, field_type=FieldType.COMPANY)

        self.owner_id = owner_id
        self.is_monopoly = is_monopoly
        self.field_dependant = field_dependant
        self.dice_dependant = dice_dependant
        self.rent = rent
        self.mortgage = mortgage
        self.filiation = filiation
        self.cost = cost
        self.mortgage_cost = mortgage_cost
        self.buyout_cost = buyout_cost
        self.filiation_cost = filiation_cost

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.field_id,
            "type": self.field_type.value,
            "company": {
                "owner_id": str(self.owner_id),
                "is_monopoly": self.is_monopoly,
                "field_dependant": self.field_dependant,
                "dice_dependant": self.dice_dependant,
                "rent": self.rent,
                "mortgage": self.mortgage,
                "filiation": self.filiation,
                "cost": self.cost,
                "mortgage_cost": self.mortgage_cost,
                "buyout_cost": self.buyout_cost,
                "filiation_cost": self.filiation_cost
            }
        }
