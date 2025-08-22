from uuid import UUID

from redis import Redis

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

    async def get_game_id(
            self,
            code: str
    ) -> UUID | None:
        try:
            return UUID(await self.get(self.key(code)))
        except ValueError:
            return
