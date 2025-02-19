from abc import ABC, abstractmethod
from typing import Dict, Any

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from app.assets.enums.field_type import FieldType
from app.assets.objects.monopoly_object import MonopolyObject


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Field(MonopolyObject, ABC):
    field_id: int
    field_type: FieldType

    __game_instance: Any = None

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any]
    ) -> Any:
        return cls(**data)

    def to_json(self) -> Dict[str, Any]:
        return {
            "field_id": self.field_id,
            "field_type": self.field_type.value
        }

    @abstractmethod
    async def on_stand(
            self,
            player: Any,
            amount: int
    ) -> None:
        pass

    @property
    def game(self) -> Any:
        return self.__game_instance

    @game.setter
    def game(self, value: Any) -> None:
        self.__game_instance = value
