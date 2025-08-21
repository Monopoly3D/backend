from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    api_key: SecretStr
    jwt_key: SecretStr
    database_dsn: SecretStr
    test_database_dsn: SecretStr | None = None
    redis_dsn: SecretStr

    s3_dsn: SecretStr
    s3_region: str = "eu-central-1"
    s3_username: SecretStr
    s3_password: SecretStr

    smtp_host: str | None = None
    smtp_port: int | None = None
    email_name: SecretStr | None = None
    email_password: SecretStr | None = None

    verification_url: str | None = None

    jwt_algorithm: str = "HS256"
