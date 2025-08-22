import string
from dataclasses import dataclass
from random import choice
from typing import Tuple, ClassVar, TYPE_CHECKING

from app.assets.objects.redis import RedisObject

if TYPE_CHECKING:
    from app.assets.redis.codes import CodesController


@dataclass
class GameCode(RedisObject, str):
    __characters: ClassVar[Tuple[str | int, ...]] = (
            tuple(string.ascii_uppercase)
            + tuple(str(__number) for __number in range(10))
    )

    code: str
    _controller: 'CodesController'

    @classmethod
    def from_json(
            cls,
            code: str,
            *,
            controller: 'CodesController'
    ) -> 'GameCode':
        return cls(
            code,
            _controller=controller
        )

    def to_json(self) -> str:
        return self.code

    async def save(self) -> None:
        await self._controller.set(self._controller.key(self.code), self.to_json())

    async def exists(self) -> bool:
        return await self._controller.exists(self._controller.key(self.code))

    async def clear(self) -> None:
        await self._controller.remove(self._controller.key(self.code))

    @classmethod
    def random(
            cls,
            *,
            controller: 'CodesController',
            length: int = 6
    ) -> 'GameCode':
        return GameCode(
            "".join(choice(cls.__characters) for _ in range(length)),
            _controller=controller
        )
