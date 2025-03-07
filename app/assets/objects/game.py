import asyncio
import json
import random
from asyncio import CancelledError, Task
from dataclasses import field as dataclass_field
from typing import Dict, Any, List, Tuple, ClassVar, Type, TypeVar
from uuid import UUID

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.api.v1.controllers.connections import ConnectionsController
from app.api.v1.controllers.redis import RedisController
from app.api.v1.exceptions.websocket.field_already_owned import FieldAlreadyOwnedError
from app.api.v1.exceptions.websocket.field_not_found import FieldNotFoundError
from app.api.v1.exceptions.websocket.game_invalid_action import GameInvalidActionError
from app.api.v1.exceptions.websocket.invalid_field_type import InvalidFieldTypeError
from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.server.game_ask_player_on_auction import ServerGameAskPlayerOnAuctionPacket
from app.api.v1.packets.server.game_countdown_start import ServerGameCountdownStartPacket
from app.api.v1.packets.server.game_countdown_stop import ServerGameCountdownStopPacket
from app.api.v1.packets.server.game_move import ServerGameMovePacket
from app.api.v1.packets.server.game_players_refused_auction import ServerGamePlayersRefusedAuctionPacket
from app.api.v1.packets.server.game_start import ServerGameStartPacket
from app.api.v1.packets.server.player_put_field_for_auction import ServerPlayerPutFieldForAuctionPacket
from app.assets.actions.action import Action
from app.assets.actions.buy_field import BuyFieldAction
from app.assets.actions.buy_field_on_auction import BuyFieldOnAuctionAction
from app.assets.actions.casino import CasinoAction
from app.assets.actions.contract import ContractAction
from app.assets.actions.move import MoveAction
from app.assets.actions.pay_chance import PayChanceAction
from app.assets.actions.pay_prison import PayPrisonAction
from app.assets.actions.pay_rent import PayRentAction
from app.assets.actions.pay_tax import PayTaxAction
from app.assets.actions.prison import PrisonAction
from app.assets.controllers.fields import FieldsController
from app.assets.controllers.monopolies import MonopoliesController
from app.assets.controllers.players import PlayersController
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
from app.assets.parameters import Parameters

T = TypeVar('T', bound=Action)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Game(RedisObject):
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
        ActionType.MOVE: MoveAction,
        ActionType.BUY_FIELD: BuyFieldAction,
        ActionType.BUY_FIELD_ON_AUCTION: BuyFieldOnAuctionAction,
        ActionType.PAY_RENT: PayRentAction,
        ActionType.PAY_CHANCE: PayChanceAction,
        ActionType.PAY_TAX: PayTaxAction,
        ActionType.PAY_PRISON: PayPrisonAction,
        ActionType.PRISON: PrisonAction,
        ActionType.CASINO: CasinoAction,
        ActionType.CONTRACT: ContractAction
    }

    game_id: UUID
    is_started: bool = False
    round: int = 0
    move: int = 0
    min_players: int = Parameters.MIN_PLAYERS
    max_players: int = Parameters.MAX_PLAYERS
    start_delay: int = Parameters.START_DELAY

    action: T | None = None
    start_bonus: int = Parameters.START_BONUS
    start_reward: int = Parameters.START_REWARD
    start_bonus_round_amount: int = Parameters.START_BONUS_ROUND_AMOUNT
    auction_minimum_bet: int = Parameters.AUCTION_MINIMUM_BET

    players: PlayersController = dataclass_field(default_factory=PlayersController)
    fields: FieldsController = dataclass_field(default_factory=FieldsController)
    monopolies: MonopoliesController = dataclass_field(default_factory=MonopoliesController)
    map_path: str = Parameters.DEFAULT_MAP_PATH

    __controller_instance: RedisController | None = None
    __start_task_name: str | None = None

    def __post_init__(self):
        self.players.setup(game_instance=self)
        self.fields.setup(game_instance=self)
        self.monopolies.setup(self.fields.list, game_instance=self)

        self.__start_task_name = f"start:{self.game_id}"

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
            *,
            connections: ConnectionsController | None = None
    ) -> Any:
        players: List[Dict[str, Any]] = data["players"]
        fields: List[Dict[str, Any]] = data["fields"]

        del data["players"]
        del data["fields"]
        data["action"] = cls.get_field(data)

        game: Game = cls(**data)

        game.players.setup(players, game_instance=game, connections=connections)
        game.fields.setup(fields, game_instance=game)
        game.monopolies.setup(game.fields.list, game_instance=game)

        return game

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
            "auction_minimum_bet": self.auction_minimum_bet,
            "players": self.players.to_json(),
            "fields": self.fields.to_json()
        }

    async def send(
            self,
            packet: ServerPacket
    ) -> None:
        for player in self.players.list:
            await player.send(packet)

    @property
    def controller(self) -> RedisController:
        return self.__controller_instance

    @controller.setter
    def controller(self, value: RedisController) -> None:
        super().__init__(value.REDIS_KEY.format(game_id=self.game_id), value)
        self.__controller_instance = value

    async def start(self) -> None:
        self.is_started = True
        self.action = MoveAction()

        #  self.players.shuffle()  TESTING
        self.fields = self.get_map(self.map_path)
        self.monopolies.setup(self.fields.list, game_instance=self)

        await self.send(
            ServerGameStartPacket(
                self.game_id,
                self.players.list,
                self.fields.list
            )
        )
        await self.send(
            ServerGameMovePacket(
                self.game_id,
                self.round,
                self.move
            )
        )

        await self.save()

    async def start_countdown(self) -> None:
        task: Task | None = self.get_start_task()

        if task is not None:
            task.cancel()

        task: Task = asyncio.create_task(self.__delayed_start(), name=self.__start_task_name)
        await self.send(
            ServerGameCountdownStartPacket(
                self.game_id,
                self.start_delay
            )
        )

        await task

    async def stop_countdown(self) -> None:
        await self.send(
            ServerGameCountdownStopPacket(
                self.game_id
            )
        )

        task: Task | None = self.get_start_task()

        if task is not None:
            task.cancel()

    async def next(self) -> None:
        player: Player = self.players.get_by_move()

        if player.double_amount <= 0 or player.prison >= 0:
            self.move += 1

            if self.move >= self.players.size:
                self.move = 0
                self.round += 1

        player.double_amount = 0

        self.action = MoveAction()

        await self.send(
            ServerGameMovePacket(
                self.game_id,
                self.round,
                self.move
            )
        )

    async def start_auction(
            self,
            player: Player,
            field: Field
    ) -> None:
        if field is None:
            raise FieldNotFoundError("Field with provided index was not found")

        if not isinstance(field, Company):
            raise InvalidFieldTypeError("Provided field is not a company")

        if field.owner_id is not None:
            raise FieldAlreadyOwnedError("Provided field is already owned")

        cost: int = field.cost + self.auction_minimum_bet
        auction_players: List[UUID] = self.get_auction_players(
            self.players.get_players_with_sufficient_balance(cost),
            player.player_id
        )

        self.action = BuyFieldOnAuctionAction(field=field.field_id, cost=cost, players=auction_players)

        await self.send(
            ServerPlayerPutFieldForAuctionPacket(
                self.game_id,
                player.player_id,
                field.field_id,
                cost
            )
        )

        await self.ask_next_player_on_auction()

    async def ask_next_player_on_auction(self) -> None:
        if not isinstance(self.action, BuyFieldOnAuctionAction):
            raise GameInvalidActionError("Game with provided UUID awaits different action")

        if len(self.action.players) == 0:
            await self.send(
                ServerGamePlayersRefusedAuctionPacket(
                    self.game_id
                )
            )

            await self.next()
            return

        self.action.player = self.action.player + 1
        if self.action.player >= len(self.action.players):
            self.action.player = 0

        player: Player = self.players.get_by_auction()

        await self.send(
            ServerGameAskPlayerOnAuctionPacket(
                self.game_id,
                player.player_id,
                self.action.field,
                self.action.cost
            )
        )

    def get_map(
            self,
            map_path: str
    ) -> FieldsController:
        with open(map_path, "r") as file:
            data: List[Dict[str, Any]] = json.load(file)

        fields: FieldsController = FieldsController()

        for index, field in enumerate(data):
            field.update({"field_id": index})

            new_field: Field | None = self.get_field(field)

            if new_field is None:
                continue

            new_field.game = self
            fields.add(new_field)

        fields.setup(game_instance=self)
        return fields

    def get_start_task(self) -> Task | None:
        tasks: List[Task] = [task for task in asyncio.all_tasks() if task.get_name() == self.__start_task_name]

        if not tasks:
            return

        return tasks[0]

    @staticmethod
    def roll_dices(
            *,
            amount: int = 2
    ) -> Tuple[int, ...]:
        if amount == 2:
            return 11, 9

        return tuple(random.randint(1, 6) for _ in range(amount))

    @staticmethod
    def get_auction_players(
            players: List[Player],
            player_id: UUID | None = None
    ) -> List[UUID]:
        return [
            auction_player.player_id for auction_player in players
            if player_id is None or auction_player.player_id != player_id
        ]

    async def __delayed_start(self) -> None:
        try:
            await asyncio.sleep(self.start_delay)
            await self.start()
        except CancelledError:
            pass

    @classmethod
    def get_field(
            cls,
            data: Dict[str, Any]
    ) -> Field | None:
        if "field_type" not in data:
            return

        return cls.FIELDS[FieldType(data.get("field_type"))].from_json(data)

    @classmethod
    def get_action(
            cls,
            data: Dict[str, Any]
    ) -> Action | None:
        if "action_type" not in data:
            return

        return cls.ACTIONS[ActionType(data.get("action_type"))].from_json(data)
