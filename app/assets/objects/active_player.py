from typing import Any, Dict
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.assets.objects.object import GameObject


@dataclass
class ActivePlayer(GameObject):
    game_id: UUID
    player_id: UUID
    is_host: bool

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "is_host": self.is_host
        }
