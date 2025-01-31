from typing import Dict, Any, Annotated
from uuid import UUID, uuid4

from fastapi import Depends
from redis.asyncio import Redis

from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.game import Game
from app.dependencies import Dependency


class GamesController(RedisController):
    REDIS_KEY = "games:{game_id}"

    async def create_game(self) -> Game:
        game: Game = Game(
            uuid4(),
            controller=self
        )
        await game.save()

        return game

    async def get_game(
            self,
            game_id: UUID
    ) -> Game:
        game: Dict[str, Any] | None = await self.get(self.REDIS_KEY.format(game_id=game_id))

        if game is None:
            raise NotFoundError("Game with provided UUID was not found")

        return Game(
            game.get("id"),
            is_started=game.get("is_started"),
            controller=self
        )

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        if not await self.exists(self.REDIS_KEY.format(game_id=game_id)):
            raise NotFoundError("Game with provided UUID was not found")

        await self.remove(self.REDIS_KEY.format(game_id=game_id))

    @staticmethod
    async def dependency(redis: Annotated[Redis, Depends(Dependency.redis)]) -> 'GamesController':
        return GamesController(redis)

    @staticmethod
    async def websocket_dependency(redis: Annotated[Redis, Depends(Dependency.redis_websocket)]) -> 'GamesController':
        return GamesController(redis)
