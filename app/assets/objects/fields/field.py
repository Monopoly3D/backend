from abc import ABC, abstractmethod
from typing import Dict, Any, ClassVar

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.object import GameObject


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Field(GameObject, ABC):
    FIELD_TYPE: ClassVar[FieldType]
    field_id: int

    __game_instance: Any = None

    @abstractmethod
    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        pass

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return {"field_id": self.field_id, "field_type": self.FIELD_TYPE.value}

    @classmethod
    def unpack(cls, data: Dict[str, Any]) -> 'Field':
        return cls.from_json(data)

    def pack(self) -> Dict[str, Any]:
        return {"field_id": self.field_id, "field_type": self.FIELD_TYPE.value, **self.to_json()}

    @property
    def game(self) -> Any:
        return self.__game_instance

    @game.setter
    def game(self, value: Any) -> None:
        self.__game_instance = value
