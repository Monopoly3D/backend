from typing import Dict, Any
from uuid import UUID, uuid4

from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.not_found_error import NotFoundError
from app.assets.game import Game


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
