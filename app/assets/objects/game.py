import json
from typing import Dict, Any, List, Tuple
from uuid import UUID

from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.redis import RedisController
from app.assets.objects.field import Field
from app.assets.objects.player import Player
from app.assets.objects.redis import RedisObject


class Game(RedisObject):
    DEFAULT_MAP_PATH: str = "app/assets/maps/default_map.json"
    MAX_PLAYERS: int = 5

    def __init__(
            self,
            game_id: UUID,
            *,
            is_started: bool | None = None,
            current_round: int | None = None,
            current_move: int | None = None,
            has_start_bonus: bool | None = None,
            players: List[Player] | None = None,
            fields: List[Field] | None = None,
            controller: RedisController
    ) -> None:
        self.game_id = game_id
        self.is_started = is_started or False
        self.round = current_round or 0
        self.move = current_move or 0
        self.has_start_bonus = has_start_bonus or True

        self.__players: Dict[UUID, Player] = {player.player_id: player for player in players}
        self.__fields = fields or self.default_map()

        super().__init__(controller.REDIS_KEY.format(game_id=game_id), controller)

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
            *,
            controller: RedisController,
            connections: ConnectionsController
    ) -> Any:
        if "id" not in data:
            return

        try:
            game_id = UUID(data.get("id"))
        except ValueError:
            return

        players: List[Player] = []
        fields: List[Field] = []

        for data_player in data.get("players", []):
            player: Player | None = Player.from_json(data_player)

            if player is None:
                continue

            player.connection = connections.connections.get(player.player_id)
            players.append(player)

        for data_field in data.get("fields", []):
            if "type" not in data_field:
                continue

            field: Field | None = Field.from_json(data_field)

            if field is None:
                continue

            fields.append(field)

        return cls(
            game_id,
            is_started=data.get("is_started"),
            current_round=data.get("current_round"),
            current_move=data.get("current_move"),
            has_start_bonus=data.get("has_start_bonus"),
            players=players,
            fields=fields,
            controller=controller
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": str(self.game_id),
            "is_started": self.is_started,
            "round": self.round,
            "move": self.move,
            "has_start_bonus": self.has_start_bonus,
            "players": self.players_json,
            "fields": self.fields_json
        }

    @property
    def players(self) -> List[Player]:
        return list(self.__players.values())

    @property
    def fields(self) -> List[Field]:
        return self.__fields

    @property
    def players_json(self) -> List[Dict[str, Any]]:
        return [player.to_json() for player in self.players]

    @property
    def fields_json(self) -> List[Dict[str, Any]]:
        return [field.to_json() for field in self.fields]

    def add_player(
            self,
            player: Player
    ) -> None:
        self.__players.update({player.player_id: player})

    def has_player(
            self,
            player_id: UUID
    ) -> bool:
        return player_id in self.__players

    def remove_player(
            self,
            player_id: UUID
    ) -> None:
        self.__players.pop(player_id)

    def get_connections(self) -> Tuple[WebSocket, ...]:
        return filter(lambda connection: connection is not None, map(lambda player: player.connection, self.players)),

    @classmethod
    def default_map(cls) -> List[Field]:
        return cls.__get_map(cls.DEFAULT_MAP_PATH)

    @classmethod
    def __get_map(
            cls,
            game_path: str
    ) -> List[Field]:
        with open(game_path, "r") as file:
            data: List[Dict[str, Any]] = json.load(file)

        fields: List[Field] = []

        for index, field in enumerate(data):
            field.update({"id": index})

            new_field: Field | None = Field.from_json(field)

            if new_field is None:
                continue

            fields.append(new_field)

        return fields
