from random import shuffle
from typing import Dict, List, Any, Tuple
from uuid import UUID

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.models.response.player import PlayerResponseModel
from app.assets.controllers.context import ContextController
from app.assets.objects.player import Player


class PlayersController(ContextController):
    def __init__(self) -> None:
        self.__players: Dict[UUID, Player] = {}
        self.game_instance: Any = None

    def setup(
            self,
            players: List[Dict[str, Any]] | None = None,
            *,
            game_instance: Any = None,
            connections: ConnectionsController | None = None
    ) -> None:
        self.game_instance = game_instance

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
            self.__players[player.player_id] = player

    def get(
            self,
            uuid: UUID
    ) -> Player | None:
        return self.__players.get(uuid)

    def get_by_move(
            self,
            move: int
    ) -> Player | None:
        try:
            return self.list[move]
        except IndexError:
            return

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

    def to_json(self) -> List[Dict[str, Any]]:
        return [player.to_json() for player in self.list]

    def shuffle(self) -> None:
        players_items: List[Tuple[UUID, Player]] = list(self.__players.items())
        shuffle(players_items)
        self.__players = dict(players_items)
