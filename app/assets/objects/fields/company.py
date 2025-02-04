from typing import List, Any, Dict
from uuid import UUID

from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field
from app.assets.objects.player import Player


class Company(Field):
    FIELD_TYPE = FieldType.COMPANY

    def __init__(
            self,
            field_id: int,
            *,
            owner_id: UUID | None = None,
            is_monopoly: bool | None = None,
            field_dependant: bool | None = None,
            dice_dependant: bool | None = None,
            rent: List[int],
            mortgage: int | None = None,
            filiation: int | None = None,
            cost: int,
            mortgage_cost: int,
            buyout_cost: int,
            filiation_cost: int
    ) -> None:
        super().__init__(field_id)

        self.owner_id = owner_id
        self.is_monopoly = is_monopoly or False
        self.field_dependant = field_dependant or False
        self.dice_dependant = dice_dependant or False
        self.rent = rent
        self.mortgage = mortgage or -1
        self.filiation = filiation or 0
        self.cost = cost
        self.mortgage_cost = mortgage_cost
        self.buyout_cost = buyout_cost
        self.filiation_cost = filiation_cost

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        if "company" not in data:
            return

        company: Dict[str, Any] = data["company"]
        owner_id: str | None = company.get("owner_id")

        if owner_id is not None:
            try:
                owner_id: UUID = UUID(owner_id)
            except ValueError:
                pass

        return cls(
            data.get("id"),
            owner_id=owner_id,
            is_monopoly=company.get("is_monopoly"),
            field_dependant=company.get("field_dependant"),
            dice_dependant=company.get("dice_dependant"),
            rent=company.get("rent"),
            mortgage=company.get("mortgage"),
            filiation=company.get("filiation"),
            cost=company.get("cost"),
            mortgage_cost=company.get("mortgage_cost"),
            buyout_cost=company.get("buyout_cost"),
            filiation_cost=company.get("filiation_cost")
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.field_id,
            "type": self.FIELD_TYPE.value,
            "company": {
                "owner_id": str(self.owner_id) if self.owner_id else None,
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

    async def on_stand(
            self,
            player: Player,
            amount: int
    ) -> None:
        if self.owner_id is None:
            print("You can buy it")
            return

        if self.owner_id == player.player_id:
            self.game.awaiting_move = True
            return

        if self.mortgage >= 0:
            self.game.awaiting_move = True
            return

    def stand_cost(
            self,
            amount: int
    ) -> int:
        if self.field_dependant:
            field_count: int = 0
            for field in self.game.fields:
                if field.FIELD_TYPE == FieldType.COMPANY and field.rent_dependant and field.owner_id == self.owner_id:
                    field_count += 1
            try:
                return self.rent[field_count - 1]
            except IndexError:
                return 0

        if self.dice_dependant:
            field_count: int = 0
            for field in self.game.fields:
                if field.FIELD_TYPE == FieldType.COMPANY and field.dice_dependant and field.owner_id == self.owner_id:
                    field_count += 1
            try:
                return self.rent[field_count - 1] * amount
            except IndexError:
                return 0

        if self.is_monopoly:
            if self.filiation == 0:
                return self.rent[0] * 2

            try:
                return self.rent[self.filiation]
            except IndexError:
                return 0

        return self.rent[0]
