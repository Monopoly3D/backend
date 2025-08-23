from uuid import UUID

from redis.asyncio import Redis

from app.assets.redis.abstract import RedisController


class HostsController(RedisController):
    def __init__(
            self,
            redis: Redis
    ) -> None:
        super().__init__(redis)

    def key(self, host_id: UUID) -> str:
        return f"hosts:{host_id}"

    async def create_host(
            self,
            game_id: UUID,
            host_id: UUID
    ) -> None:
        await self.set(self.key(host_id), str(game_id))

    async def get_game_id(
            self,
            host_id: UUID
    ) -> UUID | None:
        try:
            return UUID(await self.get(self.key(host_id)))
        except (ValueError, TypeError):
            return

    async def exists_host(
            self,
            host_id: UUID
    ) -> bool:
        return await self.exists(self.key(host_id))

    async def remove_host(
            self,
            host_id: UUID
    ) -> None:
        await self.remove(self.key(host_id))
