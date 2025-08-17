from enum import StrEnum


class Permission(StrEnum):
    VIEW_OWN_USER = "view_own_user"

    CREATE_GAMES = "create_games"
    VIEW_GAMES = "view_games"
    REMOVE_GAMES = "remove_games"
    JOIN_GAMES = "join_games"
    LEAVE_GAMES = "leave_games"
    REMOVE_OWN_GAMES = "remove_own_games"
