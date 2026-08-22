from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Research Collaboration Agent"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/research_agent"
    secret_key: str = "change-me-in-production-use-a-strong-secret"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    allowed_origins: list[str] = ["http://localhost:3000"]
    redis_url: str | None = None
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
