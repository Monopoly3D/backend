from typing import Dict, Any
from uuid import UUID

from app.assets.redis.abstract import RedisController
from app.assets.objects.active_player import ActivePlayer


class ActivePlayersController(RedisController):
    def key(
            self,
            player_id: UUID
    ) -> str:
        return f"player:{player_id}"

    async def create_active_player(
            self,
            game_id: UUID,
            player_id: UUID,
            *,
            is_host: bool
    ) -> None:
        await self.set(
            self.key(player_id),
            ActivePlayer(
                game_id=game_id,
                player_id=player_id,
                is_host=is_host
            ).to_json()
        )

    async def get_active_player(
            self,
            player_id: UUID
    ) -> ActivePlayer | None:
        active_player_json: Dict[str, Any] = await self.get(self.key(player_id))

        if active_player_json is None:
            return

        return ActivePlayer(**active_player_json)

    async def exists_active_player(
            self,
            player_id: UUID
    ) -> bool:
        return await self.exists(self.key(player_id))

    async def remove_active_player(
            self,
            player_id: UUID
    ) -> None:
        await self.remove(self.key(player_id))
