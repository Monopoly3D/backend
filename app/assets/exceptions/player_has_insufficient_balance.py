from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class PlayerHasInsufficientBalanceError(GameError):
    status_code = game_status.G_4303_PLAYER_HAS_INSUFFICIENT_BALANCE
