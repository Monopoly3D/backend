from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class FieldIsMonopolyError(GameError):
    status_code = game_status.G_4407_FIELD_IS_MONOPOLY
