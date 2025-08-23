from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class PlayerAlreadyHostError(GameError):
    status_code = game_status.G_4306_PLAYER_ALREADY_HOST
