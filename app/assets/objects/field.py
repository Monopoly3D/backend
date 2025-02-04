from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type

from app.assets.enums.field_type import FieldType
from app.assets.objects.monopoly_object import MonopolyObject
from app.assets.objects.player import Player


class Field(MonopolyObject, ABC):
    FIELD_TYPE: FieldType

    def __init__(
            self,
            field_id: int
    ) -> None:
        self.field_id = field_id

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        if "id" not in data or "type" not in data:
            return

        return cls.get_class(data.get("type")).from_json(data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.field_id,
            "type": self.FIELD_TYPE.value
        }

    @abstractmethod
    async def on_stand(
            self,
            player: Player
    ) -> None:
        pass

    @classmethod
    def get_class(
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
