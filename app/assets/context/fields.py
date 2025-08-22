from typing import Dict, List, Any, TYPE_CHECKING, Optional

from app.api.v1.models.response.field import FieldResponseModel
from app.api.v1.packets.server.player_lose_mortgaged_field import ServerPlayerLoseMortgagedFieldPacket
from app.assets.context.abstract import Context
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.abstract import AbstractField
from app.assets.objects.fields.company import Company

if TYPE_CHECKING:
    from app.assets.objects.game import Game


class Fields(Context):
    def __init__(self) -> None:
        self._fields: List[AbstractField] = []
        self._game: Optional['Game'] = None

    def init(
            self,
            fields: List[Dict[str, Any]] | None,
            *,
            game: 'Game'
    ) -> None:
        self._fields.clear()
        self._game = game

        if fields is None:
            return

        for field_json in fields:
            field: AbstractField | None = self.game.get_field(field_json)

            if field is None:
                continue

            self.add(field)

    def to_json(self) -> List[Dict[str, Any]]:
        return [field.pack() for field in self.list]

    @property
    def game(self) -> Optional['Game'] | None:
        return self._game

    @property
    def list(self) -> List[AbstractField]:
        return self._fields

    @property
    def models_list(self) -> List[FieldResponseModel]:
        return [FieldResponseModel.from_field(field) for field in self.list]

    @property
    def companies(self) -> List[Company]:
        return list(filter(lambda field: isinstance(field, Company), self.list))

    @property
    def size(self) -> int:
        return len(self._fields)

    @property
    def prison(self) -> int:
        return [field.FIELD_TYPE for field in self._fields].index(FieldType.PRISON)

    def add(
            self,
            field: AbstractField
    ) -> None:
        field.game = self.game
        self._fields.append(field)

    def get(
            self,
            index: int
    ) -> AbstractField | None:
        return self._fields[index] if index < len(self._fields) else None

    async def decrease_all_mortgages(self) -> None:
        has_any_mortgaged_fields: bool = False

        for field in self.list:
            if not isinstance(field, Company) or field.mortgage < 0:
                continue

            has_any_mortgaged_fields: bool = True
            field.mortgage -= 1

            if field.mortgage:
                continue

            field.mortgage = -1
            field.owner_id = None

            await self.game.send(
                ServerPlayerLoseMortgagedFieldPacket(
                    self.game.game_id,
                    field.field_id
                )
            )

        if has_any_mortgaged_fields:
            await self.game.save()
