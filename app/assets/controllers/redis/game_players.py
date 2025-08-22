from typing import Dict, Any
from uuid import UUID

from app.assets.controllers.base_redis import RedisController
from app.assets.objects.game_player import GamePlayer


class GamePlayersController(RedisController):
    def key(
            self,
            player_id: UUID
    ) -> str:
        return f"player:{player_id}"

    async def create_game_player(
            self,
            game_id: UUID,
            player_id: UUID,
            *,
            is_host: bool
    ) -> None:
        await self.set(
            self.key(player_id),
            GamePlayer(
                game_id=game_id,
                player_id=player_id,
                is_host=is_host
            ).to_json()
        )

    async def get_game_player(
            self,
            player_id: UUID
    ) -> GamePlayer | None:
        game_player_json: Dict[str, Any] = await self.get(self.key(player_id))

        if game_player_json is None:
            return

        return GamePlayer(**game_player_json)

    async def exists_game_player(
            self,
            player_id: UUID
    ) -> bool:
        return await self.exists(self.key(player_id))

    async def remove_game_player(
            self,
            player_id: UUID
    ) -> None:
        await self.remove(self.key(player_id))
