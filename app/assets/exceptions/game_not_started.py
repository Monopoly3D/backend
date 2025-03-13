from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class GameNotStartedError(GameError):
    status_code = game_status.G_4202_GAME_NOT_STARTED
