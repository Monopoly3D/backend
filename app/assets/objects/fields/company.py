from dataclasses import field as dataclass_field
from typing import List, Any, Dict
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.server.player_can_buy_field import ServerPlayerCanBuyFieldPacket
from app.api.v1.packets.server.player_must_pay_rent import ServerPlayerMustPayRentPacket
from app.assets.enums.company_type import CompanyType
from app.assets.enums.field_type import FieldType
from app.assets.enums.monopoly_type import MonopolyType
from app.assets.objects.actions.buy_field import BuyFieldAction
from app.assets.objects.actions.pay_rent import PayRentAction
from app.assets.objects.fields.abstract import AbstractField
from app.assets.parameters import Parameters


@dataclass
class Company(AbstractField):
    FIELD_TYPE = FieldType.COMPANY

    owner_id: UUID | None = None
    monopoly_type: MonopolyType = MonopolyType.BASE
    company_type: CompanyType = CompanyType.BASE

    rent: List[int] = dataclass_field(default_factory=list)
    mortgage: int = -1
    filiation: int = 0
    cost: int = 0
    mortgage_cost: int = 0
    buyout_cost: int = 0
    filiation_cost: int = 0

    __monopoly: Any = dataclass_field(default=None, repr=False)

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        if "company" not in data:
            return

        return cls(
            data.get("field_id"),
            data.get("field_type"),
            **data.get("company")
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "company": {
                "owner_id": str(self.owner_id) if self.owner_id else None,
                "monopoly_type": self.monopoly_type.value,
                "company_type": self.company_type.value,
                "rent": self.rent,
                "mortgage": self.mortgage,
                "filiation": self.filiation,
                "cost": self.cost,
                "mortgage_cost": self.mortgage_cost,
                "buyout_cost": self.buyout_cost,
                "filiation_cost": self.filiation_cost
            }
        }

    @property
    def monopoly(self) -> Any | None:
        return self.__monopoly

    @monopoly.setter
    def monopoly(self, value: Any):
        self.__monopoly = value

    @property
    def is_monopoly(self) -> bool:
        if self.monopoly is None:
            return False

        return self.monopoly.is_monopoly

    @is_monopoly.setter
    def is_monopoly(self, value: bool) -> None:
        if self.monopoly is None:
            return

        for company in self.monopoly.companies:
            company.is_monopoly = value

    @property
    def field_dependant(self) -> bool:
        return self.company_type == CompanyType.FIELD_DEPENDANT

    @property
    def dice_dependant(self) -> bool:
        return self.company_type == CompanyType.DICE_DEPENDANT

    @property
    def is_mortgaged(self) -> bool:
        return self.mortgage >= 0

    @is_mortgaged.setter
    def is_mortgaged(self, value: bool) -> None:
        if value and not self.is_mortgaged:
            self.mortgage = Parameters.MORTGAGE_MOVE_LIMIT
        elif not value and self.is_mortgaged:
            self.mortgage = -1

    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        if self.owner_id is None:
            self.game.action = BuyFieldAction(cost=self.cost)
            await player.send(
                ServerPlayerCanBuyFieldPacket(self.game.game_id, player.player_id, self.field_id, self.cost)
            )
            return

        if self.owner_id == player.player_id or self.mortgage >= 0:
            await self.game.next()
            return

        stand_amount: int = self.stand_amount(amount)

        self.game.action = PayRentAction(amount=stand_amount)
        await player.send(
            ServerPlayerMustPayRentPacket(self.game.game_id, player.player_id, self.field_id, stand_amount)
        )

    def stand_amount(
            self,
            amount: int
    ) -> int:
        if self.field_dependant:
            field_count: int = 0
            for field in self.game.fields.list:
                if field.field_type == FieldType.COMPANY and field.field_dependant and field.owner_id == self.owner_id:
                    field_count += 1
            try:
                return self.rent[field_count - 1]
            except IndexError:
                return 0

        if self.dice_dependant:
            field_count: int = 0
            for field in self.game.fields.list:
                if field.field_type == FieldType.COMPANY and field.dice_dependant and field.owner_id == self.owner_id:
                    field_count += 1
            try:
                return self.rent[field_count - 1] * amount
            except IndexError:
                return 0

        if self.monopoly is not None and self.monopoly.is_monopoly:
            if self.filiation == 0:
                return self.rent[0] * 2

            try:
                return self.rent[self.filiation]
            except IndexError:
                return 0

        return self.rent[0]
