from dataclasses import field as dataclass_field
from typing import List, Any, Dict
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.api.v1.packets.server.player_can_buy_field import ServerPlayerCanBuyFieldPacket
from app.api.v1.packets.server.player_gain_monopoly import ServerPlayerGainMonopolyPacket
from app.api.v1.packets.server.player_lose_monopoly import ServerPlayerLoseMonopolyPacket
from app.api.v1.packets.server.player_must_pay_rent import ServerPlayerMustPayRentPacket
from app.assets.actions.buy_field import BuyFieldAction
from app.assets.actions.pay_rent import PayRentAction
from app.assets.enums.company_type import CompanyType
from app.assets.enums.field_type import FieldType
from app.assets.enums.monopoly_type import MonopolyType
from app.assets.objects.fields.field import Field


@dataclass
class Company(Field):
    FIELD_TYPE = FieldType.COMPANY

    owner_id: UUID | None = None
    monopoly_type: MonopolyType = MonopolyType.BASE
    company_type: CompanyType = CompanyType.BASE

    is_monopoly: bool = False
    rent: List[int] = dataclass_field(default_factory=list)
    mortgage: int = -1
    filiation: int = 0
    cost: int = 0
    mortgage_cost: int = 0
    buyout_cost: int = 0
    filiation_cost: int = 0

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
                "is_monopoly": self.is_monopoly,
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
    def field_dependant(self) -> bool:
        return self.company_type == CompanyType.FIELD_DEPENDANT

    @property
    def dice_dependant(self) -> bool:
        return self.company_type == CompanyType.DICE_DEPENDANT

    async def set_new_owner_id(
            self,
            new_owner_id: UUID | None = None
    ) -> None:
        previous_owner_id = self.owner_id

        if previous_owner_id == new_owner_id:
            return

        fields: List[Company] = self.game.monopolies.get_fields(self.monopoly_type)

        was_monopoly: bool = self.game.monopolies.is_monopoly(fields)
        self.owner_id = new_owner_id
        is_monopoly: bool = self.game.monopolies.is_monopoly(fields)

        if not was_monopoly and is_monopoly:
            self.game.monopolies.set_monopoly(fields, True)

            await self.game.send(
                ServerPlayerGainMonopolyPacket(
                    self.game.game_id,
                    new_owner_id,
                    self.monopoly_type
                )
            )
        elif was_monopoly and not is_monopoly:
            self.game.monopolies.set_monopoly(fields, False)

            await self.game.send(
                ServerPlayerLoseMonopolyPacket(
                    self.game.game_id,
                    previous_owner_id,
                    self.monopoly_type
                )
            )

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

        if self.is_monopoly:
            if self.filiation == 0:
                return self.rent[0] * 2

            try:
                return self.rent[self.filiation]
            except IndexError:
                return 0

        return self.rent[0]
