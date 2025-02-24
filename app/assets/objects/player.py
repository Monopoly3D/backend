from typing import Any, Dict, Tuple
from uuid import UUID

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from starlette.websockets import WebSocket

from app.api.v1.exceptions.websocket.field_already_owned import FieldAlreadyOwnedError
from app.api.v1.exceptions.websocket.field_not_found import FieldNotFoundError
from app.api.v1.exceptions.websocket.field_not_owned import FieldNotOwnedError
from app.api.v1.exceptions.websocket.game_invalid_action import GameInvalidActionError
from app.api.v1.exceptions.websocket.invalid_field_type import InvalidFieldTypeError
from app.api.v1.exceptions.websocket.not_enough_balance import NotEnoughBalanceError
from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.server.player_buy_field import ServerPlayerBuyFieldPacket
from app.api.v1.packets.server.player_got_start_bonus import ServerPlayerGotStartBonusPacket
from app.api.v1.packets.server.player_move import ServerPlayerMovePacket
from app.api.v1.packets.server.player_pay_rent import ServerPlayerPayRentPacket
from app.api.v1.packets.server.player_pay_tax import ServerPlayerPayTaxPacket
from app.api.v1.packets.server.player_ready import ServerPlayerReadyPacket
from app.assets.actions.action import Action
from app.assets.actions.pay_rent import PayRentAction
from app.assets.actions.pay_tax import PayTaxAction
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field
from app.assets.objects.fields.tax import Tax
from app.assets.objects.monopoly_object import MonopolyObject
from app.assets.parameters import Parameters


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Player(MonopolyObject):
    player_id: UUID
    username: str
    balance: int = Parameters.DEFAULT_PLAYER_BALANCE
    field: int = 0
    is_ready: bool = False
    is_playing: bool = True
    is_imprisoned: bool = False
    double_amount: int = 0
    contract_amount: int = 0

    __connection_instance: WebSocket | None = None
    __game_instance: Any = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "player_id": str(self.player_id),
            "username": self.username,
            "balance": self.balance,
            "field": self.field,
            "is_ready": self.is_ready,
            "is_playing": self.is_playing,
            "is_imprisoned": self.is_imprisoned,
            "double_amount": self.double_amount,
            "contract_amount": self.contract_amount
        }

    async def send(
            self,
            packet: ServerPacket
    ) -> None:
        if self.connection is not None:
            await self.connection.send_text(packet.pack())

    @property
    def connection(self) -> WebSocket | None:
        return self.__connection_instance

    @connection.setter
    def connection(self, value: WebSocket | None) -> None:
        self.__connection_instance = value

    @property
    def game(self) -> Any:
        return self.__game_instance

    @game.setter
    def game(self, value: Any) -> None:
        self.__game_instance = value

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
            dices: Tuple[int, int]
    ) -> None:
        amount: int = 5  # sum(dices)

        self.field += amount
        got_start_bonus: bool = (
                self.field >= self.game.fields.size
                and self.game.start_bonus_round_amount < self.game.round
        )

        self.field %= self.game.fields.size
        await self.game.send(ServerPlayerMovePacket(self.game.game_id, self.player_id, dices, self.field))

        if got_start_bonus:
            self.balance += amount
            await self.game.send(ServerPlayerGotStartBonusPacket(self.game.game_id, self.player_id, self.balance))

        field: Field = self.game.fields.get(self.field)
        await field.on_stand(self, amount)

    async def buy_field(
            self,
            field: int
    ) -> None:
        field: Field | None = self.game.fields.get(field)

        if field is None:
            raise FieldNotFoundError("Field with provided index was not found")

        if not isinstance(field, Company):
            raise InvalidFieldTypeError("Provided field is not a company")

        if field.owner_id is not None:
            raise FieldAlreadyOwnedError("Provided field is already owned")

        if field.cost > self.balance:
            raise NotEnoughBalanceError("Player has insufficient balance")

        field.owner_id = self.player_id
        self.balance -= field.cost

        await self.game.send(
            ServerPlayerBuyFieldPacket(
                self.game.game_id,
                self.player_id,
                field.field_id,
                self.balance
            )
        )

    async def pay_rent(
            self,
            field: int
    ) -> None:
        field: Field | None = self.game.fields.get(field)

        if field is None:
            raise FieldNotFoundError("Field with provided index was not found")

        if not isinstance(field, Company):
            raise InvalidFieldTypeError("Provided field is not a company")

        if field.owner_id is None:
            raise FieldNotOwnedError("Provided field is not owned")

        if field.owner_id == self.player_id:
            raise FieldAlreadyOwnedError("Provided field is already owned")

        action: Action = self.game.action

        if not isinstance(action, PayRentAction):
            raise GameInvalidActionError("Game with provided UUID awaits different action")

        if action.amount > self.balance:
            raise NotEnoughBalanceError("Player has insufficient balance")

        owner: Player = self.game.players.get(field.owner_id)

        self.balance -= action.amount
        owner.balance += action.amount

        await self.game.send(
            ServerPlayerPayRentPacket(
                self.game.game_id,
                self.player_id,
                owner.player_id,
                field.field_id,
                self.balance,
                owner.balance
            )
        )

    async def pay_tax(
            self,
            field: int
    ) -> None:
        field: Field | None = self.game.fields.get(field)

        if field is None:
            raise FieldNotFoundError("Field with provided index was not found")

        if not isinstance(field, Tax):
            raise InvalidFieldTypeError("Provided field is not a tax field")

        action: Action = self.game.action

        if not isinstance(action, PayTaxAction):
            raise GameInvalidActionError("Game with provided UUID awaits different action")

        if action.amount > self.balance:
            raise NotEnoughBalanceError("Player has insufficient balance")

        self.balance -= action.amount

        await self.game.send(
            ServerPlayerPayTaxPacket(self.game.game_id, self.player_id, self.balance)
        )
