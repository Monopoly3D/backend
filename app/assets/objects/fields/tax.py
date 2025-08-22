from typing import Any, Dict

from pydantic.dataclasses import dataclass

from app.api.v1.packets.server.player_must_pay_tax import ServerPlayerMustPayTaxPacket
from app.assets.objects.actions.pay_tax import PayTaxAction
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


@dataclass
class Tax(Field):
    FIELD_TYPE = FieldType.TAX

    tax_amount: int = 0

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        if "tax" not in data:
            return

        return cls(
            data.get("field_id"),
            data.get("field_type"),
            **data.get("tax")
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "tax": {
                "tax_amount": self.tax_amount
            }
        }

    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        self.game.action = PayTaxAction(amount=self.tax_amount)

        await self.game.send(
            ServerPlayerMustPayTaxPacket(self.game.game_id, player.player_id, self.tax_amount)
        )
