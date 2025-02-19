from enum import StrEnum


class ActionType(StrEnum):
    MOVE = "move"
    BUY_FIELD = "buy_field"
    BUY_FIELD_ON_AUCTION = "buy_field_on_auction"
    PAY_RENT = "pay_rent"
    PAY_CHANCE = "pay_chance"
    PAY_TAX = "pay_tax"
    PAY_PRISON = "pay_prison"
    PRISON_ACTION = "prison"
    CASINO_ACTION = "casino"
    CONTRACT_ACTION = "contract"
