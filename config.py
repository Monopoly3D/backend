from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    api_key: SecretStr
    jwt_key: SecretStr
    database_dsn: SecretStr
    test_database_dsn: SecretStr | None = None
    redis_dsn: SecretStr

    smtp_host: str | None = None
    smtp_port: int | None = None

    no_reply_email_sender: SecretStr | None = None
    no_reply_email_password: SecretStr | None = None
    verification_url: str | None = None

    jwt_algorithm: str = "HS256"
