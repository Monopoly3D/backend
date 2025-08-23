from uuid import UUID

from redis import Redis

from app.assets.objects.code import GameCode
from app.assets.redis.abstract import RedisController


class CodesController(RedisController):
    def __init__(
            self,
            redis: Redis
    ) -> None:
        super().__init__(redis)

    def key(
            self,
            code: str
    ) -> str:
        return f"codes:{code}"

    async def create_code(
            self,
            game_id: UUID,
            code: GameCode
    ) -> None:
        await self.set(self.key(code), str(game_id))

    async def get_game_id(
            self,
            code: str
    ) -> UUID | None:
        try:
            return UUID(await self.get(self.key(code)))
        except ValueError:
            return

    async def exists_code(
            self,
            code: str
    ) -> bool:
        return await self.exists(self.key(code))

    async def remove_code(
            self,
            code: str
    ) -> None:
        await self.remove(self.key(code))
