from typing import Dict, Any
from uuid import UUID

from redis import Redis

from app.assets.controllers.redis.codes import CodesController
from app.assets.controllers.connections import ConnectionsController
from app.assets.controllers.base_redis import RedisController
from app.assets.controllers.redis.active_players import ActivePlayersController
from app.assets.objects.game import Game
from app.assets.objects.active_player import ActivePlayer


class GamesController(RedisController):
    def __init__(
            self,
            redis: Redis
    ) -> None:
        super().__init__(redis)
        self._codes_controller = CodesController(redis)
        self._active_players_controller = ActivePlayersController(redis)

    def key(self, game_id: UUID) -> str:
        return f"games:{game_id}"

    async def create_game(
            self,
            host_id: UUID,
            player_amount: int
    ) -> Game:
        game = Game(
            controller=self,
            host_id=host_id,
            player_amount=player_amount
        )

        await game.save()
        await self._codes_controller.save_code(game.code, game.game_id)
        await self._active_players_controller.create_active_player(game.game_id, host_id, is_host=True)

        return game

    async def create_active_player(
            self,
            game_id: UUID,
            player_id: UUID,
            *,
            is_host: bool
    ) -> None:
        await self._active_players_controller.create_active_player(
            game_id,
            player_id,
            is_host=is_host
        )

    async def get_game(
            self,
            game_id: UUID,
            connections: ConnectionsController | None = None
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
            connections: ConnectionsController | None = None
    ) -> Game | None:
        game_id: UUID | None = await self._codes_controller.get_game_id(code)

        if game_id is None:
            return

        return await self.get_game(game_id, connections)

    async def get_game_by_player(
            self,
            player_id: UUID,
            connections: ConnectionsController | None = None
    ) -> Game | None:
        active_player: ActivePlayer | None = await self._active_players_controller.get_active_player(player_id)

        if active_player is None:
            return

        return await self.get_game(active_player.game_id, connections)

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

    async def is_playing(
            self,
            player_id: UUID
    ) -> bool:
        return await self._active_players_controller.exists_active_player(player_id)

    async def remove_game(
            self,
            game_id: UUID
    ) -> None:
        game: Game = await self.get_game(game_id, None)

        for player_id in game.players.ids:
            await self._active_players_controller.remove_active_player(player_id)

        await self._codes_controller.remove_code(await self.get_game_code(game_id))
        await self.remove(self.key(game_id))
