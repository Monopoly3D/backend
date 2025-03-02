from enum import StrEnum


class CompanyType(StrEnum):
    BASE = "base"
    FIELD_DEPENDANT = "field_dependant"
    DICE_DEPENDANT = "dice_dependant"
