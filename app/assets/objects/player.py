from typing import Any, Dict, Tuple, List, TYPE_CHECKING
from uuid import UUID

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from starlette.websockets import WebSocket

from app.api.v1.exceptions.websocket.invalid_packet_data import InvalidPacketDataError
from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.server.game_move import ServerGameMovePacket
from app.api.v1.packets.server.player_accept_auction import ServerPlayerAcceptAuctionPacket
from app.api.v1.packets.server.player_accept_prison import ServerPlayerAcceptPrisonPacket
from app.api.v1.packets.server.player_buy_field import ServerPlayerBuyFieldPacket
from app.api.v1.packets.server.player_buy_field_on_auction import ServerPlayerBuyFieldOnAuctionPacket
from app.api.v1.packets.server.player_buy_filiation import ServerPlayerBuyFiliationPacket
from app.api.v1.packets.server.player_buyout_field import ServerPlayerBuyoutFieldPacket
from app.api.v1.packets.server.player_got_start_bonus import ServerPlayerGotStartBonusPacket
from app.api.v1.packets.server.player_mortgage_field import ServerPlayerMortgageFieldPacket
from app.api.v1.packets.server.player_move import ServerPlayerMovePacket
from app.api.v1.packets.server.player_must_pay_prison import ServerPlayerMustPayPrisonPacket
from app.api.v1.packets.server.player_pay_prison import ServerPlayerPayPrisonPacket
from app.api.v1.packets.server.player_pay_rent import ServerPlayerPayRentPacket
from app.api.v1.packets.server.player_pay_tax import ServerPlayerPayTaxPacket
from app.api.v1.packets.server.player_play_casino import ServerPlayerPlayCasinoPacket
from app.api.v1.packets.server.player_ready import ServerPlayerReadyPacket
from app.api.v1.packets.server.player_refuse_auction import ServerPlayerRefuseAuctionPacket
from app.api.v1.packets.server.player_refuse_casino import ServerPlayerRefuseCasinoPacket
from app.api.v1.packets.server.player_sell_filiation import ServerPlayerSellFiliationPacket
from app.assets.objects.actions.abstract import AbstractAction
from app.assets.objects.actions.buy_field_on_auction import BuyFieldOnAuctionAction
from app.assets.objects.actions.move import MoveAction
from app.assets.objects.actions.pay_prison import PayPrisonAction
from app.assets.objects.actions.pay_rent import PayRentAction
from app.assets.objects.actions.pay_tax import PayTaxAction
from app.assets.exceptions.field_already_filiated import FieldAlreadyFiliatedError
from app.assets.exceptions.field_already_mortgaged import FieldAlreadyMortgagedError
from app.assets.exceptions.field_already_owned import FieldAlreadyOwnedError
from app.assets.exceptions.field_is_monopoly import FieldIsMonopolyError
from app.assets.exceptions.field_is_not_monopoly import FieldIsNotMonopolyError
from app.assets.exceptions.field_not_found import FieldNotFoundError
from app.assets.exceptions.field_not_mortgaged import FieldNotMortgagedError
from app.assets.exceptions.field_not_owned import FieldNotOwnedError
from app.assets.exceptions.game_invalid_action import GameInvalidActionError
from app.assets.exceptions.invalid_field_type import InvalidFieldTypeError
from app.assets.exceptions.invalid_filiation import InvalidFiliationError
from app.assets.exceptions.player_has_insufficient_balance import PlayerHasInsufficientBalanceError
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.abstract import AbstractField
from app.assets.objects.fields.tax import Tax
from app.assets.objects.object import GameObject
from app.assets.parameters import Parameters

if TYPE_CHECKING:
    from app.assets.objects.game import Game


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Player(GameObject):
    player_id: UUID
    username: str
    _game: 'Game'

    balance: int = Parameters.DEFAULT_PLAYER_BALANCE
    field: int = 0
    is_ready: bool = False
    is_playing: bool = True
    prison: int = -1
    double_amount: int = 0
    contract_amount: int = 0

    _connection: WebSocket | None = None

    @classmethod
    def new(
            cls,
            player_id: UUID,
            username: str,
            *,
            game: 'Game',
            connection: WebSocket | None
    ) -> 'Player':
        return cls(
            player_id,
            username,
            _game=game,
            _connection=connection
        )

    @classmethod
    def from_json(
            cls,
            player_json: Dict[str, Any],
            *,
            game: 'Game',
            connection: WebSocket | None
    ) -> 'Player':
        return cls(
            **player_json,
            _game=game,
            _connection=connection
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "username": self.username,
            "balance": self.balance,
            "field": self.field,
            "is_ready": self.is_ready,
            "is_playing": self.is_playing,
            "prison": self.prison,
            "double_amount": self.double_amount,
            "contract_amount": self.contract_amount
        }

    @property
    def game(self) -> 'Game':
        return self._game

    @property
    def connection(self) -> WebSocket | None:
        return self._connection

    @connection.setter
    def connection(self, websocket: WebSocket) -> None:
        self._connection = websocket

    @property
    def is_imprisoned(self) -> bool:
        return self.prison >= 0

    @property
    def has_to_redeem_from_prison(self) -> bool:
        return self.prison >= 3

    @property
    def got_double(self) -> bool:
        return self.double_amount > 0

    async def send(
            self,
            packet: ServerPacket
    ) -> None:
        if self.connection is not None:
            await self.connection.send_text(packet.pack())

    async def set_ready(
            self,
            is_ready: bool
    ) -> None:
        self.is_ready = is_ready
        await self.game.send(
            ServerPlayerReadyPacket(
                self.game.game_id,
                self.player_id,
                self.is_ready
            )
        )

    async def move(
            self,
            dices: Tuple[int, ...],
            *,
            consider_double: bool = True
    ) -> None:
        amount: int = sum(dices)

        self.field += amount
        got_start_bonus: bool = (
                self.field >= self.game.fields.size
                and self.game.start_bonus_round_amount < self.game.round
        )

        got_double: bool = dices[0] == dices[1]

        self.field %= self.game.fields.size
        await self.game.send(
            ServerPlayerMovePacket(
                self.game.game_id,
                self.player_id,
                dices,
                self.field
            )
        )

        if got_start_bonus:
            self.balance += amount
            await self.game.send(
                ServerPlayerGotStartBonusPacket(
                    self.game.game_id,
                    self.player_id,
                    self.balance
                )
            )

        if got_double and consider_double:
            self.double_amount += 1
        else:
            self.double_amount = 0

        field: AbstractField = self.game.fields.list[self.field]
        await field.on_stand(self, amount)

    async def buy_field(
            self,
            field: int | None = None
    ) -> None:
        company: Company = self.__get_company(field)

        await self.__buy_field(company)

        await self.game.send(
            ServerPlayerBuyFieldPacket(
                self.game.game_id,
                self.player_id,
                company.field_id,
                self.balance
            )
        )

        await self.game.next()

    async def buy_field_on_auction(
            self,
            field: int,
            cost: int | None = None
    ) -> None:
        company: Company = self.__get_company(field)

        await self.__buy_field(company, cost)

        await self.game.send(
            ServerPlayerBuyFieldOnAuctionPacket(
                self.game.game_id,
                self.player_id,
                company.field_id,
                self.balance
            )
        )

        await self.game.next()

    async def put_field_on_auction(
            self,
            field: int | None = None
    ) -> None:
        company: Company = self.__get_company(field)

        await self.game.start_auction(self, company)

    async def accept_auction(
            self
    ) -> None:
        action: AbstractAction | None = self.game.action

        if not isinstance(action, BuyFieldOnAuctionAction):
            raise GameInvalidActionError("Game with provided UUID awaits different action")

        if len(action.players) == 1:
            await self.buy_field_on_auction(action.field, action.cost)
            return

        action.cost += self.game.auction_minimum_bet

        action.players = self.game.get_auction_players(
            self.game.players.get_players_with_sufficient_balance(
                action.cost,
                players=[self.game.players.get(player_id) for player_id in action.players]
            )
        )

        await self.game.send(
            ServerPlayerAcceptAuctionPacket(
                self.game.game_id,
                self.player_id,
                action.cost
            )
        )

        await self.game.ask_next_player_on_auction()

    async def refuse_auction(
            self
    ) -> None:
        action: AbstractAction | None = self.game.action

        if not isinstance(action, BuyFieldOnAuctionAction):
            raise GameInvalidActionError("Game with provided UUID awaits different action")

        action.players.pop(action.player)

        await self.game.send(
            ServerPlayerRefuseAuctionPacket(
                self.game.game_id,
                self.player_id
            )
        )

        await self.game.ask_next_player_on_auction()

    def imprison(self) -> None:
        if not self.is_imprisoned:
            self.prison = 0

    def rescue(self) -> None:
        self.prison = -1

    async def accept_prison(self) -> None:
        dices: Tuple[int, ...] = self.game.roll_dice()
        got_double: bool = dices[0] == dices[1]

        await self.game.send(
            ServerPlayerAcceptPrisonPacket(
                self.game.game_id,
                self.player_id,
                dices,
                got_double
            )
        )

        if got_double:
            self.rescue()
            await self.move(dices, consider_double=False)
            return

        self.prison += 1

        if self.has_to_redeem_from_prison:
            self.game.action = PayPrisonAction()

            await self.game.send(
                ServerPlayerMustPayPrisonPacket(
                    self.game.game_id,
                    self.player_id,
                    Parameters.DEFAULT_PRISON_ESCAPE_COST
                )
            )

            return

        await self.game.next()

    async def play_casino(
            self,
            dices: List[int]
    ) -> None:
        if self.balance < Parameters.DEFAULT_CASINO_BET:
            raise PlayerHasInsufficientBalanceError("Player has insufficient balance")

        if not (1 <= len(dices) <= 3):
            raise InvalidPacketDataError("Player must choose between 1 and 3 dices")

        if any(dice < 1 or dice > 6 for dice in dices):
            raise InvalidPacketDataError("Player must choose dices between 1 and 6")

        self.balance -= Parameters.DEFAULT_CASINO_BET

        roll: int = self.game.roll_die()
        won: bool = roll in dices
        prize: int = Parameters.DEFAULT_CASINO_BET * 6 // len(dices) if won else 0

        self.balance += prize

        await self.game.send(
            ServerPlayerPlayCasinoPacket(
                self.game.game_id,
                self.player_id,
                self.balance,
                dices,
                roll,
                won,
                prize
            )
        )

        await self.game.next()

    async def refuse_casino(self) -> None:
        await self.game.send(
            ServerPlayerRefuseCasinoPacket(
                self.game.game_id,
                self.player_id
            )
        )

        await self.game.next()

    async def pay_rent(
            self,
            field: int | None = None
    ) -> None:
        company: Company = self.__get_company(field)

        if company.owner_id is None:
            raise FieldNotOwnedError("Provided field is not owned")

        if company.owner_id == self.player_id:
            raise FieldAlreadyOwnedError("Provided field is already owned")

        action: AbstractAction = self.game.action

        if not isinstance(action, PayRentAction):
            raise GameInvalidActionError("Game with provided UUID awaits different action")

        if action.amount > self.balance:
            raise PlayerHasInsufficientBalanceError("Player has insufficient balance")

        owner: Player = self.game.players.get(company.owner_id)

        self.balance -= action.amount
        owner.balance += action.amount

        await self.game.send(
            ServerPlayerPayRentPacket(
                self.game.game_id,
                self.player_id,
                owner.player_id,
                company.field_id,
                self.balance,
                owner.balance
            )
        )

        await self.game.next()

    async def pay_tax(self) -> None:
        self.__get_tax(self.field)

        action: AbstractAction = self.game.action

        if not isinstance(action, PayTaxAction):
            raise GameInvalidActionError("Game with provided UUID awaits different action")

        if action.amount > self.balance:
            raise PlayerHasInsufficientBalanceError("Player has insufficient balance")

        self.balance -= action.amount

        await self.game.send(
            ServerPlayerPayTaxPacket(
                self.game.game_id,
                self.player_id,
                self.balance
            )
        )

        await self.game.next()

    async def pay_prison(self) -> None:
        if self.balance < Parameters.DEFAULT_PRISON_ESCAPE_COST:
            raise PlayerHasInsufficientBalanceError("Player has insufficient balance")

        self.balance -= Parameters.DEFAULT_PRISON_ESCAPE_COST
        self.rescue()

        await self.send(
            ServerPlayerPayPrisonPacket(
                self.game.game_id,
                self.player_id,
                self.balance
            )
        )

        self.game.action = MoveAction()

        await self.send(
            ServerGameMovePacket(
                self.game.game_id,
                self.player_id,
                self.game.round,
                self.game.move
            )
        )

    async def mortgage_field(
            self,
            field: int
    ) -> None:
        company: Company = self.__get_company(field)

        if company.owner_id != self.player_id:
            raise FieldNotOwnedError("Provided field is not owned")

        if company.is_mortgaged:
            raise FieldAlreadyMortgagedError("Field is already mortgaged")

        if company.is_monopoly:
            raise FieldIsMonopolyError("Field is a monopoly")

        self.balance += company.mortgage_cost
        company.is_mortgaged = True

        await self.send(
            ServerPlayerMortgageFieldPacket(
                self.game.game_id,
                self.player_id,
                company.field_id,
                self.balance
            )
        )

    async def buyout_field(
            self,
            field: int
    ) -> None:
        company: Company = self.__get_company(field)

        if company.owner_id != self.player_id:
            raise FieldNotOwnedError("Provided field is not owned")

        if not company.is_mortgaged:
            raise FieldNotMortgagedError("Field is not mortgaged")

        if company.is_monopoly:
            raise FieldIsMonopolyError("Field is a monopoly")

        if self.balance < company.buyout_cost:
            raise PlayerHasInsufficientBalanceError("Player has insufficient balance")

        self.balance -= company.buyout_cost
        company.is_mortgaged = False

        await self.send(
            ServerPlayerBuyoutFieldPacket(
                self.game.game_id,
                self.player_id,
                company.field_id,
                self.balance
            )
        )

    async def buy_filiation(
            self,
            field: int
    ) -> None:
        company: Company = self.__get_company(field)

        if company.owner_id != self.player_id:
            raise FieldNotOwnedError("Provided field is not owned")

        if not company.is_monopoly:
            raise FieldIsNotMonopolyError("Field is not a monopoly")

        if company.is_mortgaged:
            raise FieldAlreadyMortgagedError("Field is mortgaged")

        if company.filiation >= Parameters.FILIATION_LIMIT:
            raise InvalidFiliationError("Unable to buy more filiations")

        if company.monopoly.is_filiated:
            raise FieldAlreadyFiliatedError("Monopoly is already filiated")

        if company.monopoly.lowest_filiation < company.filiation:
            raise InvalidFiliationError("Too unbalanced filiations")

        if self.balance < company.filiation_cost:
            raise PlayerHasInsufficientBalanceError("Player has insufficient balance")

        company.filiation += 1
        self.balance -= company.filiation_cost

        company.monopoly.is_filiated = True

        await self.game.send(
            ServerPlayerBuyFiliationPacket(
                self.game.game_id,
                self.player_id,
                company.field_id,
                company.filiation,
                self.balance
            )
        )

    async def sell_filiation(
            self,
            field: int
    ) -> None:
        company: Company = self.__get_company(field)

        if company.owner_id != self.player_id:
            raise FieldNotOwnedError("Provided field is not owned")

        if not company.is_monopoly:
            raise FieldIsNotMonopolyError("Field is not a monopoly")

        if company.is_mortgaged:
            raise FieldAlreadyMortgagedError("Field is mortgaged")

        if company.filiation <= 0:
            raise InvalidFiliationError("Field has no filiations to sell")

        if company.monopoly.highest_filiation > company.filiation:
            raise InvalidFiliationError("Too unbalanced filiations")

        company.filiation -= 1
        self.balance += company.filiation_cost

        await self.game.send(
            ServerPlayerSellFiliationPacket(
                self.game.game_id,
                self.player_id,
                company.field_id,
                company.filiation,
                self.balance
            )
        )

    async def __buy_field(
            self,
            company: Company,
            cost: int | None = None
    ) -> None:
        if company.owner_id is not None:
            raise FieldAlreadyOwnedError("Provided field is already owned")

        if cost is None:
            cost: int = company.cost

        if cost > self.balance:
            raise PlayerHasInsufficientBalanceError("Player has insufficient balance")

        company.owner_id = self.player_id
        self.balance -= cost

    def __get_field(
            self,
            field: int | None = None
    ) -> AbstractField:
        field: AbstractField | None = self.game.fields.get(field if field is not None else self.field)

        if field is None:
            raise FieldNotFoundError("Field with provided index was not found")

        return field

    def __get_company(
            self,
            field: int | None = None
    ) -> Company:
        field: AbstractField = self.__get_field(field)

        if not isinstance(field, Company):
            raise InvalidFieldTypeError("Provided field is not a company")

        return field

    def __get_tax(
            self,
            field: int | None = None
    ) -> Tax:
        field: AbstractField = self.__get_field(field)

        if not isinstance(field, Tax):
            raise InvalidFieldTypeError("Provided field is not a company")

        return field
