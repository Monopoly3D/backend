from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class PlayerNotFoundError(GameError):
    status_code = game_status.G_4301_PLAYER_NOT_FOUND
