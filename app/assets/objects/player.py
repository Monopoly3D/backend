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
            connection: WebSocket | None = None,
            balance: int | None = None,
            field: int | None = None,
            is_ready: bool | None = None,
            is_playing: bool | None = None,
            is_imprisoned: bool | None = None,
            double_amount: int | None = None,
            contract_amount: int | None = None,
    ) -> None:
        self.player_id = player_id
        self.username = username
        self.balance = balance or 15000
        self.field = field or 0
        self.is_ready = is_ready or False
        self.is_playing = is_playing or True
        self.is_imprisoned = is_imprisoned or False
        self.double_amount = double_amount or 0
        self.contract_amount = contract_amount or 0

        self.connection = connection
        self.game: Any = None

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
            connection: WebSocket | None = None
    ) -> Any:
        if "id" not in data or "username" not in data:
            return

        try:
            player_id: UUID = UUID(data.get("id"))
        except ValueError:
            return

        return cls(
            player_id,
            username=data.get("username"),
            connection=connection,
            balance=data.get("balance"),
            field=data.get("field"),
            is_ready=data.get("is_ready"),
            is_playing=data.get("is_playing"),
            is_imprisoned=data.get("is_imprisoned"),
            double_amount=data.get("double_amount"),
            contract_amount=data.get("contract_amount")
        )

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
