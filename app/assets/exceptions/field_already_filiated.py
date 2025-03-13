from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class FieldAlreadyFiliatedError(GameError):
    status_code = game_status.G_4408_FIELD_ALREADY_FILIATED
