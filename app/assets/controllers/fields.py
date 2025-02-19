from typing import Dict, List, Any, TypeVar

from app.api.v1.models.response.field import FieldResponseModel
from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field

T = TypeVar('T', bound=Field)


class FieldsController:
    def __init__(self) -> None:
        self.__fields: List[T] = []
        self.game_instance: Any = None

    def setup(
            self,
            fields: List[Dict[str, Any]] | None = None,
            *,
            game_instance: Any = None
    ) -> None:
        self.game_instance = game_instance

        if fields is None:
            return

        for data_field in fields:
            field: Field | None = Field.from_json(data_field)

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
    def list(self) -> List[T]:
        return self.__fields

    @property
    def models_list(self) -> List[FieldResponseModel]:
        return [FieldResponseModel.from_field(field) for field in self.list]

    @property
    def size(self) -> int:
        return len(self.__fields)

    @property
    def police(self) -> int:
        return [field.field_type for field in self.__fields].index(FieldType.POLICE)

    def to_json(self) -> List[Dict[str, Any]]:
        return [field.to_json() for field in self.list]
