from typing import Dict, Any
from uuid import UUID

from redis import Redis

from app.assets.controllers.redis.codes import CodesController
from app.assets.controllers.connections import ConnectionsController
from app.assets.controllers.base_redis import RedisController
from app.assets.objects.game import Game


class GamesController(RedisController):
    def __init__(
            self,
            redis: Redis,
            codes_controller: CodesController
    ) -> None:
        super().__init__(redis)
        self._codes_controller = codes_controller

    def key(self, game_id: UUID) -> str:
        return f"games:{game_id}"

    async def create_game(self) -> Game:
        game = Game(controller=self)

        await game.save()
        await self._codes_controller.save_code(game.code, game.game_id)

        return game

    async def get_game(
            self,
            game_id: UUID,
            connections: ConnectionsController
    ) -> Game | None:
        game_json: Dict[str, Any] | None = await self.get(self.key(game_id))

        if game_json is None:
            return

        return Game.from_json(game_json, self, connections)

    async def get_game_code(
            self,
            game_id: UUID
    ) -> str | None:
        game_json: Dict[str, Any] | None = await self.get(self.key(game_id))

        if game_json is None:
            return

        return game_json.get("code")

    async def get_game_by_code(
            self,
            code: str,
            connections: ConnectionsController
    ) -> Game | None:
        game_id: str = await self._codes_controller.get_game_id(code)

        if game_id is None:
            return

        try:
            game_id: UUID = UUID(game_id)
        except ValueError:
            return

        return await self.get_game(game_id, connections)

    async def exists_game(
            self,
            game_id: UUID
    ) -> bool:
        return await self.exists(self.key(game_id))

    async def exists_game_code(
            self,
            code: str,
    ) -> bool:
        return await self._codes_controller.exists_code(code)

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        await self._codes_controller.remove_code(await self.get_game_code(game_id))
        await self.remove(self.key(game_id))
