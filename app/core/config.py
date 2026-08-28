from functools import lru_cache
from typing import Literal

from pydantic import field_validator
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
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = "ResearchMind AI"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    frontend_url: str = "http://localhost:5173"
    neo4j_uri: str | None = None
    neo4j_username: str | None = None
    neo4j_password: str | None = None
    neo4j_database: str = "neo4j"
    storage_dir: str = "storage"
    max_upload_size_mb: int = 25
    enable_document_indexing: bool = True

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value):
        """Force PostgreSQL URLs onto SQLAlchemy's Psycopg 3 dialect.

        Render commonly supplies `postgresql://` (and older services may use
        `postgres://`). SQLAlchemy's generic PostgreSQL URL defaults to the
        psycopg2 dialect, while this project intentionally installs Psycopg 3.
        """
        if not isinstance(value, str):
            return value
        value = value.strip()
        for prefix in ("postgres://", "postgresql://"):
            if value.lower().startswith(prefix):
                return "postgresql+psycopg://" + value[len(prefix):]
        if value.lower().startswith("postgresql+psycopg2://"):
            return "postgresql+psycopg://" + value[len("postgresql+psycopg2://"):]
        return value

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on", "debug"}
        return value
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
