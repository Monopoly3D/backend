from uuid import UUID

from pydantic import BaseModel

from app.assets.objects.player import Player


class PlayerResponseModel(BaseModel):
    player_id: UUID
    username: str
    balance: int
    field: int
    is_playing: bool
    is_imprisoned: bool
    double_amount: int
    contract_amount: int

    @classmethod
    def from_player(
            cls,
            player: Player
    ) -> 'PlayerResponseModel':
        return cls(
            player_id=player.player_id,
            username=player.username,
            balance=player.balance,
            field=player.field,
            is_playing=player.is_playing,
            is_imprisoned=player.is_imprisoned,
            double_amount=player.double_amount,
            contract_amount=player.contract_amount
        )
