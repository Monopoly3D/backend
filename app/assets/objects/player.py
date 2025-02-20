from typing import Any, Dict, Tuple
from uuid import UUID

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from starlette.websockets import WebSocket

from app.api.v1.packets.base_server import ServerPacket
from app.api.v1.packets.server.player_buy_field import ServerPlayerBuyFieldPacket
from app.api.v1.packets.server.player_got_start_bonus import ServerPlayerGotStartBonusPacket
from app.api.v1.packets.server.player_move import ServerPlayerMovePacket
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field
from app.assets.objects.monopoly_object import MonopolyObject


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Player(MonopolyObject):
    player_id: UUID
    username: str
    balance: int = 15000
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
        field: Company = self.game.fields.get(field)

        field.owner_id = self.player_id
        self.balance -= field.cost

        await self.game.send(
            ServerPlayerBuyFieldPacket(self.game.game_id, self.player_id, field.field_id, self.balance)
        )
