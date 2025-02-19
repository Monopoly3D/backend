from typing import Callable, Annotated

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.api.v1.exceptions.websocket.game_already_started import GameAlreadyStartedError
from app.api.v1.exceptions.websocket.game_invalid_action import GameInvalidActionError
from app.api.v1.exceptions.websocket.game_not_found import GameNotFoundError
from app.api.v1.exceptions.websocket.game_not_started import GameNotStartedError
from app.api.v1.exceptions.websocket.invalid_packet_data import InvalidPacketDataError
from app.api.v1.exceptions.websocket.player_not_found import PlayerNotFoundError
from app.api.v1.packets.base_client import ClientPacket
from app.assets.enums.action_type import ActionType
from app.assets.objects.game import Game
from app.assets.objects.player import Player
from app.assets.objects.user import User


class WebSocketDependency:
    @staticmethod
    def get_game(
            *,
            is_started: bool | None = True,
            action: ActionType | None = None,
            has_player: bool | None = True
    ) -> Callable:
        async def __get_game(
                packet: ClientPacket,
                connections: ConnectionsController,
                games_controller: GamesController,
                user: User
        ) -> Game:
            if not hasattr(packet, "game_id"):
                raise InvalidPacketDataError("Provided packet data is invalid")

            game: Game | None = await games_controller.get_game(getattr(packet, "game_id"), connections)

            if game is None or (user.user_id not in game.players.ids and has_player):
                raise GameNotFoundError("Game with provided UUID was not found")

            if is_started is not None:
                if game.is_started and not is_started:
                    raise GameAlreadyStartedError("Game with provided UUID has already started")
                if not game.is_started and is_started:
                    raise GameNotStartedError("Game with provided UUID has not been started")

            if action is not None:
                if game.action.action_type != action:
                    raise GameInvalidActionError("Game with provided UUID awaits different action")

            return game

        return __get_game

    @staticmethod
    def get_player(
            *,
            game_has_started: bool | None = None
    ) -> Callable:
        async def __get_player(
                user: User,
                game: Annotated[Game, WebSocketDependency.get_game(is_started=game_has_started)]
        ) -> Player:
            player: Player | None = game.players.get(user.user_id)

            if player is None:
                raise PlayerNotFoundError("Player is not in game")

            return player

        return __get_player
