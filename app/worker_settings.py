from arq.connections import RedisSettings, ArqRedis
from redis.asyncio import Redis

from config import Config

config: Config = Config(_env_file=".env")

redis_dsn: str = config.redis_dsn.get_secret_value()


async def on_startup(ctx: ArqRedis) -> None:
    ctx["redis"] = Redis.from_url(redis_dsn)


class WorkerSettings:
    on_startup = on_startup

    redis_settings = RedisSettings.from_dsn(redis_dsn)
