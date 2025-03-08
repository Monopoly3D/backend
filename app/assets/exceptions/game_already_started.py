from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class GameAlreadyStartedError(GameError):
    status_code = game_status.G_4203_GAME_ALREADY_STARTED
