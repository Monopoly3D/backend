import asyncio
import json
from asyncio import CancelledError
from dataclasses import field as dataclass_field
from random import shuffle, randint
from typing import Dict, Any, List, Tuple, ClassVar, Type
from uuid import UUID

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.redis import RedisController
from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.server.game_move import ServerGameMovePacket
from app.api.v1.packets.server.game_start import ServerGameStartPacket
from app.assets.actions.action import Action
from app.assets.actions.move import Move
from app.assets.enums.action_type import ActionType
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.casino import Casino
from app.assets.objects.fields.chance import Chance
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field
from app.assets.objects.fields.police import Police
from app.assets.objects.fields.prison import Prison
from app.assets.objects.fields.start import Start
from app.assets.objects.fields.tax import Tax
from app.assets.objects.player import Player
from app.assets.objects.redis import RedisObject


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Game(RedisObject):
    DEFAULT_MAP_PATH: ClassVar[str] = "app/assets/maps/default_map.json"

    FIELDS: ClassVar[Dict[FieldType, Type[Field]]] = {
        FieldType.COMPANY: Company,
        FieldType.START: Start,
        FieldType.CHANCE: Chance,
        FieldType.TAX: Tax,
        FieldType.PRISON: Prison,
        FieldType.POLICE: Police,
        FieldType.CASINO: Casino
    }

    ACTIONS: ClassVar[Dict[ActionType, Type[Action]]] = {
        ActionType.MOVE: Move
    }

    game_id: UUID
    is_started: bool = False
    round: int = 0
    move: int = 0
    min_players: int = 1
    max_players: int = 5
    start_delay: int = 3

    action: Action | None = None
    start_bonus: int = 2000
    start_reward: int = 1000
    start_bonus_round_amount: int = 65

    players: Dict[UUID, Player] = dataclass_field(default_factory=dict)
    fields: List[Field] = dataclass_field(default_factory=list)
    map_path: str = DEFAULT_MAP_PATH

    __controller_instance: RedisController | None = None

    def __post_init__(self):
        self.__setup_players()
        self.__setup_fields()

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
            *,
            connections: ConnectionsController | None = None
    ) -> Any:
        players: Dict[UUID, Player] = {}
        fields: List[Field] = []

        data["action"] = cls.__get_field(data)

        for data_player in data.get("players", []):
            player: Player | None = Player.from_json(data_player)
            if player is None:
                continue
            player.connection = connections.connections.get(player.player_id)
            players[player.player_id] = player

        for data_field in data.get("fields", []):
            field: Field | None = cls.__get_field(data_field)
            if field is None:
                continue
            fields.append(field)

        data["players"] = players
        data["fields"] = fields

        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "is_started": self.is_started,
            "action": self.action.to_json() if self.action is not None else None,
            "round": self.round,
            "move": self.move,
            "min_players": self.min_players,
            "max_players": self.max_players,
            "start_delay": self.start_delay,
            "start_bonus": self.start_bonus,
            "start_reward": self.start_reward,
            "start_bonus_round_amount": self.start_bonus_round_amount,
            "players": [player.to_json() for player in self.players_list],
            "fields": [field.to_json() for field in self.fields]
        }

    @property
    def players_list(self) -> List[Player]:
        return list(self.players.values())

    @property
    def is_ready(self) -> bool:
        return all([player.is_ready for player in self.players_list])

    @property
    def police(self) -> int:
        return [field.field_type for field in self.fields].index(FieldType.POLICE)

    @property
    def controller(self) -> RedisController:
        return self.__controller_instance

    @controller.setter
    def controller(self, value: RedisController) -> None:
        super().__init__(value.REDIS_KEY.format(game_id=self.game_id), value)
        self.__controller_instance = value

    async def start(self) -> None:
        self.is_started = True
        self.action = Move()

        self.shuffle_players()
        self.fields = self.get_map(self.map_path)
        self.__setup_fields()

        await self.send(ServerGameStartPacket(self.game_id, self.players_list, self.fields))
        await self.send(ServerGameMovePacket(self.game_id, self.round, self.move))

        await self.save()

    async def delayed_start(self) -> None:
        try:
            await asyncio.sleep(self.start_delay)
            await self.start()
        except CancelledError:
            pass

    async def move_player(self) -> None:
        player: Player = self.players_list[self.move]
        dices: Tuple[int, int] = self.throw_dices()

        await player.move(dices)

    def add_player(
            self,
            player: Player
    ) -> None:
        player.game = self
        self.players.update({player.player_id: player})

    def get_player(
            self,
            player_id: UUID
    ) -> Player | None:
        return self.players.get(player_id)

    def has_player(
            self,
            player_id: UUID
    ) -> bool:
        return player_id in self.players

    def remove_player(
            self,
            player_id: UUID
    ) -> None:
        self.players.pop(player_id)

    def shuffle_players(self) -> None:
        players_items: List[Tuple[UUID, Player]] = list(self.players.items())
        shuffle(players_items)
        self.players = dict(players_items)

    async def send(
            self,
            packet: ServerPacket
    ) -> None:
        for player in self.players_list:
            await player.send(packet)

    def get_map(
            self,
            game_path: str
    ) -> List[Field]:
        with open(game_path, "r") as file:
            data: List[Dict[str, Any]] = json.load(file)

        fields: List[Field] = []

        for index, field in enumerate(data):
            field.update({"field_id": index})

            new_field: Field | None = self.__get_field(field)

            if new_field is None:
                continue

            new_field.game = self
            fields.append(new_field)

        return fields

    @staticmethod
    def throw_dices() -> Tuple[int, int]:
        return randint(1, 6), randint(1, 6)

    def __setup_players(self) -> None:
        for player in self.players_list:
            player.game = self

    def __setup_fields(self) -> None:
        for field in self.fields:
            field.game = self

    @classmethod
    def __get_field(
            cls,
            data: Dict[str, Any]
    ) -> Field | None:
        if "field_type" not in data:
            return

        return cls.FIELDS[FieldType(data.get("field_type"))].from_json(data)

    @classmethod
    def __get_action(
            cls,
            data: Dict[str, Any]
    ) -> Action | None:
        if "action_type" not in data:
            return

        return cls.ACTIONS[ActionType(data.get("action_type"))].from_json(data)
