from typing import Any, Dict

from pydantic.dataclasses import dataclass

from app.assets.objects.field import Field
from app.assets.objects.player import Player


@dataclass
class Tax(Field):
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
            "field_id": self.field_id,
            "field_type": self.field_type.value,
            "tax": {
                "tax_amount": self.tax_amount
            }
        }

    async def on_stand(
            self,
            player: Player
    ) -> None:
        pass
