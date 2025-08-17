import asyncio
from typing import Dict, Any, Tuple
from uuid import UUID, uuid4

from redis import Redis

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.redis import RedisController
from app.assets.objects.game import Game


class GamesController(RedisController):
    def __init__(
            self,
            redis: Redis
    ) -> None:
        super().__init__(redis)

    def redis_key(self) -> str:
        return "games:{game_id}"

    async def create_game(self) -> Game:
        game = Game(self)
        await game.save()

        return game

    async def get_game(
            self,
            game_id: UUID,
            connections: ConnectionsController
    ) -> Game | None:
        game_json: Dict[str, Any] | None = await self.get(self.redis_key().format(game_id=game_id))

        if game_json is None:
            return

        return Game.from_json(game_json, self, connections)

    async def get_games(
            self,
            connections: ConnectionsController
    ) -> Tuple[Game]:
        game_uuids: Tuple[str, ...] = await self.get_keys(pattern="games")

        games: Tuple[Any] = await asyncio.gather(
            *[self.get_game(UUID(game.split(":")[-1]), connections) for game in game_uuids]
        )

        return tuple(filter(lambda game: isinstance(game, Game), games))

    async def exists_game(
            self,
            game_id: UUID
    ) -> bool:
        return await self.exists(self.redis_key().format(game_id=game_id))

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        await self.remove(self.redis_key().format(game_id=game_id))
