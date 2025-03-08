from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class GameMaxPlayersReachedError(GameError):
    status_code = game_status.G_4206_GAME_MAX_PLAYERS_REACHED
