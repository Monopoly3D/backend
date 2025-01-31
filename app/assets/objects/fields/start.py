from app.assets.enums.field_type import FieldType
from app.assets.objects.fields.field import Field


class Start(Field):
    def __init__(
            self,
            field_id: int
    ) -> None:
        super().__init__(field_id, field_type=FieldType.START)
