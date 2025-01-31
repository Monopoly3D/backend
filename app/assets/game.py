from typing import Dict, Any
from uuid import UUID

from app.api.v1.controllers.games import GamesController
from app.assets.monopoly_object import MonopolyObject
from app.assets.redis_object import RedisObject


class Game(MonopolyObject, RedisObject):
    def __init__(
            self,
            game_id: UUID,
            *,
            is_started: bool = False,
            controller: GamesController
    ) -> None:
        self.game_id = game_id
        self.is_started = is_started

        super().__init__(controller.REDIS_KEY.format(game_id), controller)

    async def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "is_started": self.is_started
        }
