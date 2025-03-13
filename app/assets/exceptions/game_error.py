from app.assets.exceptions import game_status


class GameError(Exception):
    status_code = game_status.G_4100_BAD_REQUEST
