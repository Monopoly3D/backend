from typing import Callable, List

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.games import GamesController
from app.assets.exceptions.game_already_started import GameAlreadyStartedError
from app.assets.exceptions.game_invalid_action import GameInvalidActionError
from app.assets.exceptions.game_not_awaiting_move import GameNotAwaitingMoveError
from app.assets.exceptions.game_not_found import GameNotFoundError
from app.assets.exceptions.game_not_started import GameNotStartedError
from app.api.v1.exceptions.websocket.invalid_packet_data import InvalidPacketDataError
from app.api.v1.packets.base_client import ClientPacket
from app.assets.enums.action_type import ActionType
from app.assets.exceptions.player_already_in_game import PlayerAlreadyInGameError
from app.assets.objects.game import Game
from app.assets.objects.user import User


class WebSocketDependency:
    @staticmethod
    def get_game(
            *,
            is_started: bool | None = True,
            action: ActionType | List[ActionType] | None = None,
            has_player: bool | None = True,
            is_players_turn: bool | None = False
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

            if game.players.exists(user.user_id) and not has_player:
                raise PlayerAlreadyInGameError("You are already in game")

            if is_started is not None:
                if game.is_started and not is_started:
                    raise GameAlreadyStartedError("Game with provided UUID has already started")
                if not game.is_started and is_started:
                    raise GameNotStartedError("Game with provided UUID has not been started")

            if action is not None:
                if isinstance(action, ActionType):
                    action_list: List[ActionType] = [action]
                else:
                    action_list = action
                if game.action.ACTION_TYPE not in action_list:
                    raise GameInvalidActionError("Game with provided UUID awaits different action")

            if game.players.get_by_move().player_id != user.user_id and is_players_turn:
                raise GameNotAwaitingMoveError("Player is not awaited to move")

            return game

        return __get_game
