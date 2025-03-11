from typing import Dict, List, Any

from app.api.v1.models.response.field import FieldResponseModel
from app.api.v1.packets.server.player_lose_mortgaged_field import ServerPlayerLoseMortgagedFieldPacket
from app.assets.enums.field_type import FieldType
from app.assets.enums.monopoly_type import MonopolyType
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field
from app.assets.objects.monopoly import Monopoly


class FieldsController:
    def __init__(self) -> None:
        self.__fields: List[Field] = []
        self.__monopolies: Dict[MonopolyType, Monopoly] = {}
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

        if fields is None or self.game is None:
            return

        for data_field in fields:
            field: Field | None = self.game.get_field(data_field)

            if field is None:
                continue

            field.game = game_instance
            self.__fields.append(field)

            if not isinstance(field, Company):
                continue

            if field.monopoly_type not in self.__monopolies:
                self.__monopolies[field.monopoly_type] = Monopoly()

            self.__monopolies[field.monopoly_type].add(field.field_id)

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

    def set_monopoly_status(
            self,
            monopoly_type: MonopolyType,
            is_monopoly: bool
    ) -> None:
        for company in self.__get_companies_by_monopoly_type(monopoly_type):
            company.is_monopoly = is_monopoly

    def is_monopoly(
            self,
            monopoly_type: MonopolyType
    ) -> bool:
        companies: List[Company] = self.__get_companies_by_monopoly_type(monopoly_type)

        if not len(companies):
            return False

        return len(set(company.owner_id for company in companies)) == 1 and companies[0].owner_id is not None

    def is_filiated(
            self,
            monopoly_type: MonopolyType
    ) -> bool:
        monopoly: Monopoly | None = self.__monopolies.get(monopoly_type)

        return monopoly.is_filiated if monopoly is not None else True

    def set_filiated(
            self,
            monopoly_type: MonopolyType
    ) -> None:
        monopoly: Monopoly | None = self.__monopolies.get(monopoly_type)

        if monopoly is not None:
            monopoly.is_filiated = True

    def reset_all_filiations(self) -> None:
        for monopoly in self.__monopolies.values():
            monopoly.is_filiated = False

    def __get_companies_by_monopoly_type(
            self,
            monopoly_type: MonopolyType
    ) -> List[Company]:
        monopoly: Monopoly | None = self.__monopolies.get(monopoly_type)

        if monopoly is None:
            return []

        fields: List[Field] = [self.list[field] for field in monopoly.fields]
        companies: List[Company] = list(filter(lambda field: isinstance(field, Company), fields))

        return companies

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
