import string
from random import choice
from typing import Tuple


class GameCode(str):
    __characters: Tuple[str | int, ...] = tuple(string.ascii_uppercase) + tuple(str(__number) for __number in range(10))

    @classmethod
    def random(cls, length: int = 6) -> 'GameCode':
        return GameCode("".join(choice(cls.__characters) for _ in range(length)))
