from random import shuffle
from typing import Dict, List, Any, Tuple, TYPE_CHECKING
from uuid import UUID

from starlette.websockets import WebSocket

from app.api.v1.packets.server.player_enter_game import ServerPlayerEnterGamePacket
from app.assets.objects.connections import Connections
from app.api.v1.models.response.player import PlayerResponseModel
from app.api.v1.packets.server.player_join_game import ServerPlayerJoinGamePacket
from app.assets.objects.actions.abstract import AbstractAction
from app.assets.objects.actions.buy_field_on_auction import BuyFieldOnAuctionAction
from app.assets.context.abstract import Context
from app.assets.exceptions.game_already_started import GameAlreadyStartedError
from app.assets.objects.game import Game
from app.assets.objects.player import Player

if TYPE_CHECKING:
    from app.assets.objects.game import Game


class Players(Context):
    def __init__(self) -> None:
        self._players: Dict[UUID, Player] = {}
        self._game: Game | None = None

    def init(
            self,
            players: List[Dict[str, Any]] | None,
            *,
            game: Game,
            connections: Connections | None = None
    ) -> None:
        self._players.clear()
        self._game = game

        if players is None:
            return

        for player_json in players:
            try:
                player_id = UUID(player_json.get("player_id"))
                connection: WebSocket | None = connections.get_connection(player_id)
            except ValueError:
                connection = None

            player = Player.from_json(
                player_json,
                game=game,
                connection=connection
            )

            self.add(player)

    def to_json(self) -> List[Dict[str, Any]]:
        return [player.to_json() for player in self.list]

    @property
    def game(self) -> Game | None:
        return self._game

    @property
    def ids(self) -> List[UUID]:
        return list(self._players.keys())

    @property
    def list(self) -> List[Player]:
        return list(self._players.values())

    @property
    def models_list(self) -> List[PlayerResponseModel]:
        return [PlayerResponseModel.from_player(player) for player in self.list]

    @property
    def size(self) -> int:
        return len(self._players)

    @property
    def are_ready(self) -> bool:
        return all(player.is_ready for player in self.list)

    @property
    def current(self) -> Player | None:
        if self.game is not None:
            try:
                return self.list[self.game.move]
            except IndexError:
                return

    @property
    def current_on_auction(self) -> Player | None:
        if self.game is not None:
            action: AbstractAction | None = self.game.action

            if not isinstance(action, BuyFieldOnAuctionAction):
                return

            return self.get(action.players[action.player])

    def add(
            self,
            player: Player
    ) -> None:
        if not self.exists(player.player_id):
            self._players[player.player_id] = player

    def get(
            self,
            uuid: UUID
    ) -> Player | None:
        return self._players.get(uuid)

    def exists(
            self,
            uuid: UUID
    ) -> bool:
        return uuid in self._players

    def remove(
            self,
            uuid: UUID
    ) -> None:
        if self.exists(uuid):
            self._players.pop(uuid)

    async def join(
            self,
            player: Player
    ) -> None:
        self.add(player)

        await self.game.send(
            ServerPlayerJoinGamePacket(
                self.game.game_id,
                self.list
            )
        )

    async def enter(
            self,
            player: Player
    ) -> None:
        packet = ServerPlayerEnterGamePacket(
            self.game.game_id,
            self.game.host_id,
            self.game.code,
            self.game.player_amount
        )

        if not self.exists(player.player_id) and not self.game.is_started:
            await self.game.controller.create_active_player(
                self.game.game_id,
                player.player_id,
                is_host=player.player_id == self.game.host_id
            )

            await player.send(packet)
            await self.join(player)
        elif self.exists(player.player_id):
            self.get(player.player_id).connection = player.connection
            await player.send(packet)
        else:
            raise GameAlreadyStartedError("Game with provided UUID has already started")

    def shuffle(self) -> None:
        players_items: List[Tuple[UUID, Player]] = list(self._players.items())
        shuffle(players_items)
        self._players = dict(players_items)

    def get_players_with_sufficient_balance(
            self,
            balance: int,
            players: List[Player] | None = None
    ) -> List[Player]:
        if players is None:
            return [player for player in self.list if player.balance >= balance]

        return [player for player in players if player.balance >= balance]
