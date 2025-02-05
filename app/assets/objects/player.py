from typing import Any, Dict
from uuid import UUID

from pydantic.dataclasses import dataclass
from starlette.websockets import WebSocket

from app.assets.objects.monopoly_object import MonopolyObject


@dataclass
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
            "id": str(self.player_id),
            "username": self.username,
            "balance": self.balance,
            "field": self.field,
            "is_ready": self.is_ready,
            "is_playing": self.is_playing,
            "is_imprisoned": self.is_imprisoned,
            "double_amount": self.double_amount,
            "contract_amount": self.contract_amount
        }

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
