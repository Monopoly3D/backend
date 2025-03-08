from typing import Dict, List, Any

from app.api.v1.models.response.field import FieldResponseModel
from app.api.v1.packets.server.player_lose_mortgaged_field import ServerPlayerLoseMortgagedFieldPacket
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field


class FieldsController:
    def __init__(self) -> None:
        self.__fields: List[Field] = []
        self.__game_instance: Any = None

    @property
    def game(self) -> Any:
        return self.__game_instance

    @game.setter
    def game(self, value: Any) -> None:
        self.__game_instance = value

    def setup(
            self,
            fields: List[Dict[str, Any]] | None = None,
            *,
            game_instance: Any = None
    ) -> None:
        self.game = game_instance

        if fields is None:
            return

        if self.game is not None:
            for data_field in fields:
                field: Field | None = self.game.get_field(data_field)

                if field is None:
                    continue

                self.add(field)

    def add(
            self,
            field: Field,
            *,
            index: int | None = None
    ) -> None:
        if index is None:
            self.__fields.append(field)
        else:
            self.__fields.insert(index, field)

    def get(
            self,
            index: int
    ) -> Field | None:
        try:
            return self.__fields[index]
        except IndexError:
            return

    def exists(
            self,
            index: int
    ) -> bool:
        return 0 <= index < self.size

    def remove(
            self,
            index: int
    ) -> None:
        try:
            self.__fields.pop(index)
        except IndexError:
            return

    @property
    def list(self) -> List[Field]:
        return self.__fields

    @property
    def models_list(self) -> List[FieldResponseModel]:
        return [FieldResponseModel.from_field(field) for field in self.list]

    @property
    def size(self) -> int:
        return len(self.__fields)

    @property
    def prison(self) -> int:
        return [field.FIELD_TYPE for field in self.__fields].index(FieldType.PRISON)

    def to_json(self) -> List[Dict[str, Any]]:
        return [field.to_json() for field in self.list]

    async def decrease_mortgages(self) -> None:
        has_any_mortgaged_fields: bool = False

        for field in self.list:
            if not isinstance(field, Company):
                continue

            if field.mortgage >= 0:
                has_any_mortgaged_fields: bool = True
                field.mortgage -= 1

                if field.mortgage == 0:
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
