from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class GameCreationFailedError(GameError):
    status_code = game_status.G_4200_GAME_ERROR
