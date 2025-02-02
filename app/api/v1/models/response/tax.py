from pydantic import BaseModel

from app.assets.objects.fields.tax import Tax


class TaxResponseModel(BaseModel):
    tax_amount: int

    @classmethod
    def from_tax(
            cls,
            tax: Tax
    ) -> 'TaxResponseModel':
        return cls(tax_amount=tax.tax_amount)
