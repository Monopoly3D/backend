from typing import Dict, List, Any

from app.api.v1.models.response.field import FieldResponseModel
from app.api.v1.packets.server.player_lose_mortgaged_field import ServerPlayerLoseMortgagedFieldPacket
from app.assets.controllers.context import ContextController
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field


class FieldsController(ContextController):
    def __init__(self) -> None:
        self.__fields: List[Field] = []
        self.__game_instance: Any = None

    def to_json(self) -> List[Dict[str, Any]]:
        return [field.to_json() for field in self.list]

    @property
    def game(self) -> Any:
        return self.__game_instance

    @game.setter
    def game(self, value: Any) -> None:
        self.__game_instance = value

    @property
    def list(self) -> List[Field]:
        return self.__fields

    @property
    def models_list(self) -> List[FieldResponseModel]:
        return [FieldResponseModel.from_field(field) for field in self.list]

    @property
    def companies(self) -> List[Company]:
        return list(filter(lambda field: isinstance(field, Company), self.list))

    @property
    def size(self) -> int:
        return len(self.__fields)

    @property
    def prison(self) -> int:
        return [field.FIELD_TYPE for field in self.__fields].index(FieldType.PRISON)

    def setup(
            self,
            fields: List[Dict[str, Any]] | None = None
    ) -> None:
        self.__fields.clear()

        if fields is None or self.game is None:
            return

        for data_field in fields:
            field: Field | None = self.game.get_field(data_field)

            if field is None:
                continue

            self.add(field)

    def add(
            self,
            field: Field
    ) -> None:
        field.game = self.game
        self.__fields.append(field)

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
