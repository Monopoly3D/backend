from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class FieldNotFoundError(GameError):
    status_code = game_status.G_4402_FIELD_NOT_FOUND
