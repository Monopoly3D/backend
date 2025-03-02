from typing import Dict, List, Any, TypeVar, Set

from app.assets.enums.monopoly_type import MonopolyType
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.field import Field

T = TypeVar('T', bound=Field)


class MonopoliesController:
    def __init__(self) -> None:
        self.__monopolies: Dict[MonopolyType, Set[int]] = {}
        self.__game_instance: Any = None

    def setup(
            self,
            fields: List[T],
            *,
            game_instance: Any = None
    ) -> None:
        self.__game_instance = game_instance

        if fields is None:
            return

        if self.__game_instance is not None:
            for field in fields:
                if not isinstance(field, Company):
                    continue

                self.add(field)

    def add(
            self,
            field: Company
    ) -> None:
        if not self.exists(field.monopoly_type):
            self.__monopolies[field.monopoly_type] = set()

        self.__monopolies[field.monopoly_type].add(field.field_id)

    def get(
            self,
            monopoly_type: MonopolyType
    ) -> Set[int] | None:
        return self.__monopolies.get(monopoly_type)

    def get_fields(
            self,
            monopoly_type: MonopolyType
    ) -> List[Company]:
        fields: Set[int] | None = self.get(monopoly_type)

        if fields is None:
            return []

        return [self.__game_instance.fields.get(field) for field in fields]

    def exists(
            self,
            monopoly_type: MonopolyType
    ) -> bool:
        return monopoly_type in self.__monopolies

    def remove(
            self,
            monopoly_type: MonopolyType
    ) -> None:
        if self.exists(monopoly_type):
            self.__monopolies.pop(monopoly_type)

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
