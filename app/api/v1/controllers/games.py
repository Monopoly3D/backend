from typing import Dict, Any, Annotated
from uuid import UUID

from fastapi import Depends
from redis.asyncio import Redis

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.redis import RedisController
from app.assets.objects.game import Game
from app.dependencies import Dependency


class GamesController(RedisController):
    REDIS_KEY = "games:{game_id}"

    async def create_game(self) -> Game:
        game = Game()
        game.controller = self
        await game.save()

        return game

    async def get_game(
            self,
            game_id: UUID,
            connections: ConnectionsController
    ) -> Game | None:
        game: Dict[str, Any] | None = await self.get(self.REDIS_KEY.format(game_id=game_id))

        if game is None:
            return

        game: Game = Game.from_json(game, connections=connections)
        game.controller = self
        return game

    async def exists_game(
            self,
            game_id: UUID
    ) -> bool:
        return await self.exists(self.REDIS_KEY.format(game_id=game_id))

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        await self.remove(self.REDIS_KEY.format(game_id=game_id))

    @staticmethod
    async def dependency(redis: Annotated[Redis, Depends(Dependency.redis)]) -> 'GamesController':
        return GamesController(redis)

    @staticmethod
    async def websocket_dependency(redis: Annotated[Redis, Depends(Dependency.redis_websocket)]) -> 'GamesController':
        return GamesController(redis)
