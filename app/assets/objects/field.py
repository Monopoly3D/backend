from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, ClassVar

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.monopoly_object import MonopolyObject
from app.assets.objects.player import Player


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Field(MonopolyObject, ABC):
    FIELD_TYPE: ClassVar[FieldType]

    field_id: int
    field_type: FieldType

    __game_instance: Any = None

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls.__get_class(data.get("field_type")).from_json(data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "field_id": self.field_id,
            "field_type": self.field_type.value
        }

    @abstractmethod
    async def on_stand(
            self,
            player: Player
    ) -> None:
        pass

    @property
    def game(self) -> Any:
        return self.__game_instance

    @game.setter
    def game(self, value: Any) -> None:
        self.__game_instance = value

    @classmethod
    def __get_class(
            cls,
            field_type: FieldType | str
    ) -> Type['Field'] | None:
        if isinstance(field_type, str):
            field_type: FieldType = FieldType(field_type)

        return {field.FIELD_TYPE: field for field in cls.__get_fields()}[field_type]

    @classmethod
    def __get_fields(cls) -> List[Type['Field']]:
        subclasses: List[Type[Field]] = cls.__subclasses__()
        overall: List[Type[Field]] = []

        for subclass in subclasses:
            overall.append(subclass)
            overall.extend(subclass.__get_fields())

        return overall
