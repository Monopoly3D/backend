from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class GameNotFoundError(GameError):
    status_code = game_status.G_4201_GAME_NOT_FOUND
