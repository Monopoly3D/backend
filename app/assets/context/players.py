from random import shuffle
from typing import Dict, List, Any, Tuple
from uuid import UUID

from starlette.websockets import WebSocket

from app.api.v1.packets.server.player_enter_game import ServerPlayerEnterGamePacket
from app.assets.controllers.connections import ConnectionsController
from app.api.v1.models.response.player import PlayerResponseModel
from app.api.v1.packets.server.player_join_game import ServerPlayerJoinGamePacket
from app.assets.objects.actions.abstract import AbstractAction
from app.assets.objects.actions.buy_field_on_auction import BuyFieldOnAuctionAction
from app.assets.context.abstract import AbstractContext
from app.assets.exceptions.game_already_started import GameAlreadyStartedError
from app.assets.objects.player import Player


class Players(AbstractContext):
    def __init__(self) -> None:
        self.__players: Dict[UUID, Player] = {}
        self.__game_instance: Any = None

    def to_json(self) -> List[Dict[str, Any]]:
        return [player.to_json() for player in self.list]

    @property
    def game(self) -> Any:
        return self.__game_instance

    @game.setter
    def game(self, value: Any) -> None:
        self.__game_instance = value

    @property
    def ids(self) -> List[UUID]:
        return list(self.__players.keys())

    @property
    def list(self) -> List[Player]:
        return list(self.__players.values())

    @property
    def models_list(self) -> List[PlayerResponseModel]:
        return [PlayerResponseModel.from_player(player) for player in self.list]

    @property
    def size(self) -> int:
        return len(self.__players)

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

    def setup(
            self,
            players: List[Dict[str, Any]] | None = None,
            *,
            connections: ConnectionsController | None = None
    ) -> None:
        if players is None:
            return

        for data_player in players:
            player: Player | None = Player.from_json(data_player)

            if player is None:
                continue

            if connections is not None:
                player.connection = connections.get_connection(player.player_id)

            self.add(player)

    def add(
            self,
            player: Player
    ) -> None:
        if not self.exists(player.player_id):
            player.game = self.game
            self.__players[player.player_id] = player

    def get(
            self,
            uuid: UUID
    ) -> Player | None:
        return self.__players.get(uuid)

    def exists(
            self,
            uuid: UUID
    ) -> bool:
        return uuid in self.__players

    def remove(
            self,
            uuid: UUID
    ) -> None:
        if self.exists(uuid):
            self.__players.pop(uuid)

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
            player: Player,
            connection: WebSocket
    ) -> None:
        packet = ServerPlayerEnterGamePacket(
            self.game.game_id,
            self.game.host_id,
            self.game.code,
            self.game.player_amount
        )

        if not self.exists(player.player_id) and not self.game.is_started:
            self.game.controller.create_active_player(
                self.game.game_id,
                player.player_id,
                is_host=player.player_id == self.game.host_id
            )

            await player.send(packet)
            await self.join(player)
        elif self.exists(player.player_id):
            self.get(player.player_id).connection = connection
            await player.send(packet)
        else:
            raise GameAlreadyStartedError("Game with provided UUID has already started")

    def shuffle(self) -> None:
        players_items: List[Tuple[UUID, Player]] = list(self.__players.items())
        shuffle(players_items)
        self.__players = dict(players_items)

    def get_players_with_sufficient_balance(
            self,
            balance: int,
            players: List[Player] | None = None
    ) -> List[Player]:
        if players is None:
            return [player for player in self.list if player.balance >= balance]

        return [player for player in players if player.balance >= balance]
