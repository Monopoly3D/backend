from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    api_key: SecretStr
    jwt_key: SecretStr
    database_dsn: SecretStr
    redis_dsn: SecretStr

    jwt_algorithm: str = "HS256"
