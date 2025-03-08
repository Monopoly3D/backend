from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class FieldAlreadyOwnedError(GameError):
    status_code = game_status.G_4405_FIELD_ALREADY_OWNED
