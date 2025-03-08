from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class InvalidFiliationError(GameError):
    status_code = game_status.G_4409_INVALID_FILIATION
