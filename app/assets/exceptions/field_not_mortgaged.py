from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class FieldNotMortgagedError(GameError):
    status_code = game_status.G_4404_FIELD_NOT_MORTGAGED
