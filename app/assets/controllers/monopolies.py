from typing import Dict, List, Any

from app.assets.enums.monopoly_type import MonopolyType
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field
from app.assets.objects.monopoly import Monopoly


class MonopoliesController:
    def __init__(self) -> None:
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
            fields: List[Field],
            *,
            game_instance: Any = None
    ) -> None:
        self.game = game_instance

        if fields is None:
            return

        if self.game is not None:
            for field in fields:
                if not isinstance(field, Company):
                    continue

                self.add(field)

    def add(
            self,
            field: Company
    ) -> None:
        if not self.exists(field.monopoly_type):
            self.__monopolies[field.monopoly_type] = Monopoly()

        self.__monopolies[field.monopoly_type].add(field.field_id)

    def get(
            self,
            monopoly_type: MonopolyType
    ) -> Monopoly | None:
        return self.__monopolies.get(monopoly_type)

    def get_fields(
            self,
            monopoly_type: MonopolyType
    ) -> List[Company]:
        monopoly: Monopoly | None = self.get(monopoly_type)

        if monopoly is None:
            return []

        return [self.game.fields.get(field) for field in monopoly.fields]

    def exists(
            self,
            monopoly_type: MonopolyType
    ) -> bool:
        return monopoly_type in self.__monopolies

    def is_filiated(
            self,
            monopoly_type: MonopolyType
    ) -> bool:
        monopoly: Monopoly | None = self.get(monopoly_type)

        if monopoly is None:
            return True

        return monopoly.is_filiated

    def set_filiated(
            self,
            monopoly_type: MonopolyType
    ) -> None:
        monopoly: Monopoly | None = self.get(monopoly_type)

        if monopoly is not None:
            monopoly.is_filiated = True

    def reset_filiated(self) -> None:
        for monopoly in self.__monopolies.values():
            monopoly.is_filiated = False

    @staticmethod
    def is_monopoly(fields: List[Company]) -> bool:
        if not len(fields):
            return False

        return len(set(field.owner_id for field in fields)) == 1 and fields[0].owner_id is not None

    @staticmethod
    def set_monopoly(
            fields: List[Company],
            is_monopoly: bool
    ) -> None:
        for field in fields:
            field.is_monopoly = is_monopoly
