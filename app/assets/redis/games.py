from typing import Dict, Any
from uuid import UUID

from redis import Redis

from app.assets.objects.active_player import ActivePlayer
from app.assets.objects.connections import Connections
from app.assets.objects.game import Game
from app.assets.redis.abstract import RedisController
from app.assets.redis.active_players import ActivePlayersController
from app.assets.redis.codes import CodesController


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

    @property
    def codes_controller(self) -> CodesController:
        return self._codes_controller

    @property
    def active_players_controller(self) -> ActivePlayersController:
        return self._active_players_controller

    async def create_game(
            self,
            host_id: UUID,
            player_amount: int,
            *,
            connections: Connections
    ) -> Game:
        game = Game.new(
            host_id,
            player_amount,
            controller=self,
            connections=connections
        )

        await game.save()
        await game.code.save()

        return game

    async def create_player(
            self,
            game_id: UUID,
            player_id: UUID,
            *,
            is_host: bool
    ) -> None:
        await ActivePlayer(
            game_id=game_id,
            player_id=player_id,
            is_host=is_host,
            _controller=self.active_players_controller
        ).save()

    async def get_game(
            self,
            game_id: UUID,
            *,
            connections: Connections
    ) -> Game | None:
        game_json: Dict[str, Any] | None = await self.get(self.key(game_id))

        if game_json is None:
            return

        return Game.from_json(game_json, controller=self, connections=connections)

    async def get_game_by_code(
            self,
            code: str,
            *,
            connections: Connections
    ) -> Game | None:
        game_id: UUID | None = await self._codes_controller.get_game_id(code)

        if game_id is None:
            return

        return await self.get_game(game_id, connections=connections)

    async def get_game_by_player(
            self,
            player_id: UUID,
            *,
            connections: Connections
    ) -> Game | None:
        active_player: ActivePlayer | None = await self._active_players_controller.get_active_player(player_id)

        if active_player is None:
            return

        return await self.get_game(active_player.game_id, connections=connections)

    async def exists_game(
            self,
            game_id: UUID
    ) -> bool:
        return await self.exists(self.key(game_id))

    async def is_playing(
            self,
            player_id: UUID
    ) -> bool:
        return await self._active_players_controller.exists_active_player(player_id)

    async def remove_game(
            self,
            game_id: UUID,
            *,
            connections: Connections
    ) -> None:
        game: Game = await self.get_game(game_id, connections=connections)

        for player_id in game.players.ids:
            await ActivePlayer(
                game.game_id,
                player_id,
                is_host=game.players.get(player_id).is_host,
                _controller=self.active_players_controller
            ).clear()

        await game.code.clear()
        await game.clear()
