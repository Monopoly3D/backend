import asyncio
import json
import random
from asyncio import CancelledError, Task
from dataclasses import field as dataclass_field
from typing import Dict, Any, List, Tuple, ClassVar, Type, TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.server.game_ask_player_on_auction import ServerGameAskPlayerOnAuctionPacket
from app.api.v1.packets.server.game_ask_player_on_prison import ServerGameAskPlayerOnPrisonPacket
from app.api.v1.packets.server.game_countdown_start import ServerGameCountdownStartPacket
from app.api.v1.packets.server.game_countdown_stop import ServerGameCountdownStopPacket
from app.api.v1.packets.server.game_move import ServerGameMovePacket
from app.api.v1.packets.server.game_players_refused_auction import ServerGamePlayersRefusedAuctionPacket
from app.api.v1.packets.server.game_start import ServerGameStartPacket
from app.api.v1.packets.server.player_put_field_for_auction import ServerPlayerPutFieldForAuctionPacket
from app.assets.objects.actions.abstract import AbstractAction
from app.assets.objects.actions.buy_field import BuyFieldAction
from app.assets.objects.actions.buy_field_on_auction import BuyFieldOnAuctionAction
from app.assets.objects.actions.casino import CasinoAction
from app.assets.objects.actions.contract import ContractAction
from app.assets.objects.actions.move import MoveAction
from app.assets.objects.actions.pay_chance import PayChanceAction
from app.assets.objects.actions.pay_prison import PayPrisonAction
from app.assets.objects.actions.pay_rent import PayRentAction
from app.assets.objects.actions.pay_tax import PayTaxAction
from app.assets.objects.actions.prison import PrisonAction
from app.assets.controllers.connections import ConnectionsController
from app.assets.controllers.context.fields import FieldsController
from app.assets.controllers.context.monopolies import MonopoliesController
from app.assets.controllers.context.players import PlayersController
from app.assets.enums.action_type import ActionType
from app.assets.enums.field_type import FieldType
from app.assets.exceptions.field_already_owned import FieldAlreadyOwnedError
from app.assets.exceptions.game_invalid_action import GameInvalidActionError
from app.assets.objects.fields.casino import Casino
from app.assets.objects.fields.chance import Chance
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field
from app.assets.objects.fields.police import Police
from app.assets.objects.fields.prison import Prison
from app.assets.objects.fields.start import Start
from app.assets.objects.fields.tax import Tax
from app.assets.objects.code import GameCode
from app.assets.objects.player import Player
from app.assets.objects.redis import RedisObject
from app.assets.parameters import Parameters

if TYPE_CHECKING:
    from app.assets.controllers.redis.games import GamesController


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Game(RedisObject):
    __CODE_REGENERATION_LIMIT: ClassVar[int] = 10

    __FIELDS: ClassVar[Dict[FieldType, Type[Field]]] = {
        FieldType.COMPANY: Company,
        FieldType.START: Start,
        FieldType.CHANCE: Chance,
        FieldType.TAX: Tax,
        FieldType.PRISON: Prison,
        FieldType.POLICE: Police,
        FieldType.CASINO: Casino
    }

    __ACTIONS: ClassVar[Dict[ActionType, Type[AbstractAction]]] = {
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

    controller: Any
    host_id: UUID
    player_amount: int

    game_id: UUID = dataclass_field(default_factory=uuid4)
    code: GameCode = dataclass_field(default_factory=GameCode.random)
    is_started: bool = False
    seed: int = 1
    round: int = 0
    move: int = 0
    start_delay: int = Parameters.START_DELAY

    action: AbstractAction | None = None
    start_bonus: int = Parameters.START_BONUS
    start_reward: int = Parameters.START_REWARD
    start_bonus_round_amount: int = Parameters.START_BONUS_ROUND_AMOUNT
    auction_minimum_bet: int = Parameters.AUCTION_MINIMUM_BET

    players: PlayersController = dataclass_field(default_factory=PlayersController)
    fields: FieldsController = dataclass_field(default_factory=FieldsController)
    monopolies: MonopoliesController = dataclass_field(default_factory=MonopoliesController)

    _map_path: str = dataclass_field(default=Parameters.DEFAULT_MAP_PATH, repr=False)
    _start_task: str | None = dataclass_field(default=None, repr=False)
    _random: random.Random | None = dataclass_field(default=None, repr=False)

    def __post_init__(self):
        for _ in range(self.__CODE_REGENERATION_LIMIT):
            pass

        self.players.game = self
        self.fields.game = self
        self.monopolies.game = self

        self._start_task = f"start:{self.game_id}"
        self._random = random.Random(self.seed)

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
            controller: 'GamesController',
            connections: ConnectionsController | None = None
    ) -> Any:
        players: List[Dict[str, Any]] = data.pop("players")
        fields: List[Dict[str, Any]] = data.pop("fields")
        monopolies: Dict[str, Any] = data.pop("monopolies")

        if data.get("code") is not None:
            data["code"] = GameCode(data["code"])
        if data.get("action") is not None:
            data["action"] = cls.get_action(data["action"])

        game: Game = cls(controller=controller, **data)

        game.players.setup(players, connections=connections)
        game.fields.setup(fields)
        game.monopolies.setup(monopolies, game.fields.companies)

        return game

    def to_json(self) -> Dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "host_id": str(self.host_id),
            "code": self.code,
            "is_started": self.is_started,
            "action": self.action.pack() if self.action is not None else None,
            "round": self.round,
            "move": self.move,
            "seed": self.seed,
            "player_amount": self.player_amount,
            "start_delay": self.start_delay,
            "start_bonus": self.start_bonus,
            "start_reward": self.start_reward,
            "start_bonus_round_amount": self.start_bonus_round_amount,
            "auction_minimum_bet": self.auction_minimum_bet,
            "players": self.players.to_json(),
            "fields": self.fields.to_json(),
            "monopolies": self.monopolies.to_json()
        }

    async def save(self) -> None:
        await self.controller.set(self.controller.key(self.game_id), self.to_json())

    async def send(
            self,
            packet: ServerPacket
    ) -> None:
        for player in self.players.list:
            await player.send(packet)

    async def start(self) -> None:
        self.is_started = True
        self.action = MoveAction()

        #  self.players.shuffle()  TESTING
        self.fields = self.get_map(self._map_path)
        self.monopolies.setup(companies=self.fields.companies)

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
                self.players.current.player_id,
                self.round,
                self.move
            )
        )

        await self.save()

    async def start_countdown(self) -> None:
        task: Task | None = self.get_start_task()

        if task is not None:
            task.cancel()

        task: Task = asyncio.create_task(self.__delayed_start(), name=self._start_task)

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
        player: Player = self.players.current

        if not player.got_double or player.is_imprisoned:
            self.move += 1

            if self.move >= self.players.size:
                self.move = 0
                self.round += 1

                await self.fields.decrease_all_mortgages()
                self.monopolies.reset_all_filiations()

        next_player: Player = self.players.current

        await self.send(
            ServerGameMovePacket(
                self.game_id,
                next_player.player_id,
                self.round,
                self.move
            )
        )

        if next_player.is_imprisoned:
            self.action = PrisonAction()

            await self.send(
                ServerGameAskPlayerOnPrisonPacket(
                    self.game_id,
                    next_player.player_id,
                    Parameters.DEFAULT_PRISON_ESCAPE_COST
                )
            )
        else:
            self.action = MoveAction()

    async def start_auction(
            self,
            player: Player,
            company: Company
    ) -> None:
        if company.owner_id is not None:
            raise FieldAlreadyOwnedError("Provided field is already owned")

        cost: int = company.cost + self.auction_minimum_bet
        auction_players: List[UUID] = self.get_auction_players(
            self.players.get_players_with_sufficient_balance(cost),
            player.player_id
        )

        self.action = BuyFieldOnAuctionAction(field=company.field_id, cost=cost, players=auction_players)

        await self.send(
            ServerPlayerPutFieldForAuctionPacket(
                self.game_id,
                player.player_id,
                company.field_id,
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

        self.action.player += 1

        if self.action.player >= len(self.action.players):
            self.action.player = 0

        player: Player = self.players.current_on_auction

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

        for index, field in enumerate(data):
            field.update({"field_id": index})

        fields: FieldsController = FieldsController()
        fields.game = self
        fields.setup(data)

        return fields

    def get_start_task(self) -> Task | None:
        tasks: List[Task] = [task for task in asyncio.all_tasks() if task.get_name() == self._start_task]

        if not tasks:
            return

        return tasks[0]

    async def __delayed_start(self) -> None:
        try:
            await asyncio.sleep(self.start_delay)
            await self.start()
        except CancelledError:
            pass

    def roll_dice(
            self,
            *,
            amount: int = 2
    ) -> Tuple[int, ...]:
        return tuple(self._random.randint(1, 6) for _ in range(amount))

    def roll_die(self) -> int:
        return self._random.randint(1, 6)

    @staticmethod
    def get_auction_players(
            players: List[Player],
            player_id: UUID | None = None
    ) -> List[UUID]:
        return [
            auction_player.player_id for auction_player in players
            if player_id is None or auction_player.player_id != player_id
        ]

    @classmethod
    def get_field(
            cls,
            data: Dict[str, Any]
    ) -> Field | None:
        if "field_type" not in data:
            return

        return cls.__FIELDS[FieldType(data.get("field_type"))].from_json(data)

    @classmethod
    def get_action(
            cls,
            data: Dict[str, Any]
    ) -> AbstractAction | None:
        if "action_type" not in data:
            return

        return cls.__ACTIONS[ActionType(data.get("action_type"))].unpack(data)
