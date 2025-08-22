from typing import Any, Dict, TYPE_CHECKING
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.assets.objects.redis import RedisObject

if TYPE_CHECKING:
    from app.assets.redis.active_players import ActivePlayersController


@dataclass
class ActivePlayer(RedisObject):
    game_id: UUID
    player_id: UUID
    is_host: bool
    _controller: 'ActivePlayersController'

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
            *,
            controller: 'ActivePlayersController'
    ) -> Any:
        return cls(
            **data,
            _controller=controller
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "player_id": str(self.player_id),
            "is_host": self.is_host
        }

    async def save(self) -> None:
        await self._controller.set(self._controller.key(self.player_id), self.to_json())

    async def exists(self) -> bool:
        return await self._controller.exists(self._controller.key(self.player_id))

    async def clear(self) -> None:
        await self._controller.remove(self._controller.key(self.player_id))
