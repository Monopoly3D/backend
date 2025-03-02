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
            for data_field in fields:
                field: Field | None = self.__game_instance.get_field(data_field)

                if field is None:
                    continue

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
