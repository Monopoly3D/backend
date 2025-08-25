from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class PlayerKickHostError(GameError):
    status_code = game_status.G_4307_PLAYER_KICK_HOST
