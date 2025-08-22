from dataclasses import field as dataclass_field
from typing import Dict, Any, List
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.assets.objects.actions.abstract import AbstractAction
from app.assets.enums.action_type import ActionType


@dataclass
class BuyFieldOnAuctionAction(AbstractAction):
    ACTION_TYPE = ActionType.BUY_FIELD_ON_AUCTION

    field: int
    cost: int
    player: int = -1
    players: List[UUID] = dataclass_field(default_factory=list)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(
            field=data.get("field"),
            cost=data.get("cost"),
            player=data.get("player"),
            players=[UUID(player_id) for player_id in data.get("players", [])]
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "cost": self.cost,
            "player": self.player,
            "players": list(map(str, self.players))
        }
