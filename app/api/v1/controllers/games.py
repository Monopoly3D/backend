import asyncio
from typing import Dict, Any, Tuple
from uuid import UUID, uuid4

from redis import Redis

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.redis import RedisController
from app.assets.objects.game import Game


class GamesController(RedisController):
    REDIS_KEY = "games:{game_id}"

    def __init__(
            self,
            redis: Redis
    ) -> None:
        super().__init__(redis)
        self.games: Dict[UUID, Game] = {}

    async def create_game(self) -> Game:
        game = Game(uuid4())
        game.controller = self

        self.games[game.game_id] = game
        await game.save()

        return game

    async def get_game(
            self,
            game_id: UUID,
            connections: ConnectionsController
    ) -> Game | None:
        game: Game | None = self.games.get(game_id)

        if game is None:
            game: Dict[str, Any] | None = await self.get(self.REDIS_KEY.format(game_id=game_id))
            if game is None:
                return
            game: Game = Game.from_json(game, connections=connections)

        game.controller = self
        return game

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
        return self.games.get(game_id) or await self.exists(self.REDIS_KEY.format(game_id=game_id))

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        self.games.pop(game_id, None)
        await self.remove(self.REDIS_KEY.format(game_id=game_id))

    async def retrieve_games(
            self,
            connections: ConnectionsController
    ) -> None:
        self.games.update({game.game_id: game for game in await self.get_games(connections)})
