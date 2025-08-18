from uuid import UUID

from redis import Redis

from app.assets.controllers.base_redis import RedisController


class CodesController(RedisController):
    def __init__(
            self,
            redis: Redis
    ) -> None:
        super().__init__(redis)

    def key(self, code: str) -> str:
        return f"codes:{code}"

    async def save_code(
            self,
            code: str,
            game_id: UUID
    ) -> None:
        await self.set(self.key(code), str(game_id))

    async def get_game_id(
            self,
            code: str
    ) -> str | None:
        return await self.get(self.key(code))

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
