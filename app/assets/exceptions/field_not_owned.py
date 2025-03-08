from app.assets.exceptions import game_status
from app.assets.exceptions.game_error import GameError


class FieldNotOwnedError(GameError):
    status_code = game_status.G_4403_FIELD_NOT_OWNED
