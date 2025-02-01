from typing import Any, Dict
from uuid import UUID

from starlette.websockets import WebSocket

from app.assets.objects.monopoly_object import MonopolyObject


class Player(MonopolyObject):
    def __init__(
            self,
            player_id: UUID,
            *,
            username: str,
            connection: WebSocket,
            balance: int = 15000,
            field: int = 0,
            is_playing: bool = True,
            is_imprisoned: bool = False,
            double_amount: int = 0,
            contract_amount: int = 0
    ) -> None:
        self.player_id = player_id
        self.username = username
        self.balance = balance
        self.field = field
        self.is_playing = is_playing
        self.is_imprisoned = is_imprisoned
        self.double_amount = double_amount
        self.contract_amount = contract_amount

        self.__connection = connection

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": str(self.player_id),
            "username": self.username,
            "balance": self.balance,
            "field": self.field,
            "is_playing": self.is_playing,
            "is_imprisoned": self.is_imprisoned,
            "double_amount": self.double_amount,
            "contract_amount": self.contract_amount
        }

    @property
    def connection(self) -> WebSocket:
        return self.__connection
