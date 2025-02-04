import asyncio
import json
from asyncio import CancelledError
from random import shuffle, randint
from typing import Dict, Any, List, Tuple
from uuid import UUID

from starlette.websockets import WebSocket

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.redis import RedisController
from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.server.game_move_packet import ServerGameMovePacket
from app.api.v1.packets.server.game_start import ServerGameStartPacket
from app.assets.objects.field import Field
from app.assets.objects.player import Player
from app.assets.objects.redis import RedisObject


class Game(RedisObject):
    DEFAULT_MAP_PATH: str = "app/assets/maps/default_map.json"

    def __init__(
            self,
            game_id: UUID,
            *,
            is_started: bool | None = None,
            awaiting_move: bool | None = None,
            current_round: int | None = None,
            current_move: int | None = None,
            min_players: int | None = None,
            max_players: int | None = None,
            start_delay: int | None = None,
            start_bonus: int | None = None,
            has_start_bonus: bool | None = None,
            players: List[Player] | None = None,
            fields: List[Field] | None = None,
            controller: RedisController
    ) -> None:
        self.game_id = game_id
        self.is_started = is_started or False
        self.awaiting_move = awaiting_move or False
        self.round = current_round or 0
        self.move = current_move or 0
        self.min_players = min_players or 1
        self.max_players = max_players or 5
        self.start_delay = start_delay or 3
        self.start_bonus = start_bonus or 2000
        self.has_start_bonus = has_start_bonus or True

        self.__players: Dict[UUID, Player] = {player.player_id: player for player in players} if players else {}
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
            awaiting_move=data.get("awaiting_move"),
            current_round=data.get("current_round"),
            current_move=data.get("current_move"),
            min_players=data.get("min_players"),
            max_players=data.get("max_players"),
            start_delay=data.get("start_delay"),
            start_bonus=data.get("start_bonus"),
            has_start_bonus=data.get("has_start_bonus"),
            players=players,
            fields=fields,
            controller=controller
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": str(self.game_id),
            "is_started": self.is_started,
            "awaiting_move": self.awaiting_move,
            "round": self.round,
            "move": self.move,
            "min_players": self.min_players,
            "max_players": self.max_players,
            "start_delay": self.start_delay,
            "start_bonus": self.start_bonus,
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

    async def start(self) -> None:
        self.is_started = True
        self.awaiting_move = True
        self.shuffle_players()

        await self.send(ServerGameStartPacket(self.game_id, self.players))
        await self.send(ServerGameMovePacket(self.game_id, self.round, self.move))

        await self.save()

    async def delayed_start(self) -> None:
        try:
            await asyncio.sleep(self.start_delay)
            await self.start()
        except CancelledError:
            pass

    async def move_player(self) -> None:
        player: Player = self.players[self.move]

        dices: Tuple[int, int] = self.throw_dices()
        amount: int = 8  # sum(dices)

        player.field += amount
        if player.field >= len(self.fields):
            player.field %= len(self.fields)
            if self.has_start_bonus:
                player.balance += self.start_bonus

        field: Field = self.fields[player.field]

        self.move += 1
        if self.move >= len(self.players):
            self.move = 0
            self.round += 1

    def add_player(
            self,
            player: Player
    ) -> None:
        self.__players.update({player.player_id: player})

    def get_player(
            self,
            player_id: UUID
    ) -> Player | None:
        return self.__players.get(player_id)

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

    def shuffle_players(self) -> None:
        players_items: List[Tuple[UUID, Player]] = list(self.__players.items())
        shuffle(players_items)
        self.__players = dict(players_items)

    async def send(
            self,
            packet: ServerPacket
    ) -> None:
        for connection in self.connections:
            await connection.send_text(packet.pack())

    @property
    def is_ready(self) -> bool:
        return all([player.is_ready for player in self.players])

    @property
    def connections(self) -> Tuple[WebSocket, ...]:
        return tuple(
            filter(lambda connection: connection is not None, map(lambda player: player.connection, self.players))
        )

    @classmethod
    def default_map(cls) -> List[Field]:
        return cls.__get_map(cls.DEFAULT_MAP_PATH)

    @staticmethod
    def throw_dices() -> Tuple[int, int]:
        return randint(1, 6), randint(1, 6)

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
