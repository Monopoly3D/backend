from typing import Dict, Any

from pydantic import BaseModel, model_serializer

from app.api.v1.models.response.company import CompanyResponseModel
from app.api.v1.models.response.tax import TaxResponseModel
from app.assets.enums.field_type import FieldType
from app.assets.objects.field import Field
from app.assets.objects.fields.company import Company
from app.assets.objects.fields.tax import Tax


class FieldResponseModel(BaseModel):
    field_id: int
    field_type: FieldType

    company: CompanyResponseModel | None
    tax: TaxResponseModel | None

    @classmethod
    def from_field(
            cls,
            field: Field
    ) -> 'FieldResponseModel':
        return cls(
            field_id=field.field_id,
            field_type=field.field_type,
            company=CompanyResponseModel.from_company(field) if isinstance(field, Company) else None,
            tax=TaxResponseModel.from_tax(field) if isinstance(field, Tax) else None,
        )

    @model_serializer()
    def serialize_model(self) -> Dict[str, Any]:
        model: Dict[str, Any] = {
            "field_id": self.field_id,
            "field_type": self.field_type
        }

        if self.company:
            model["company"] = self.company
        if self.tax:
            model["tax"] = self.tax

        return model
