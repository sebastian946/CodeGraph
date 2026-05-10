
from pydantic_settings import BaseSettings, SettingsConfigDict
import redis


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    REDIS_URL: str
    ENVIRONMENT: str
    LOG_LEVEL: str = "INFO"
    GITHUB_APP_ID: int
    GITHUB_INSTALLATION_ID: int
    GITHUB_PRIVATE_KEY_PATH: str = "config/codegraphtest.2026-05-08.private-key.pem"
    FERNET_KEY: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


def get_redis_client() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.REDIS_URL)