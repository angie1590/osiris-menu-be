"""Configuración por variables de entorno (pydantic-settings).

Sin secretos hardcodeados: los valores por defecto son placeholders de desarrollo
equivalentes al `docker-compose.yml` raíz y siempre se sobrescriben por entorno.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://osiris:osiris_dev_pass@localhost:5433/osiris_menu"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    APP_ENV: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # TTL de idempotencia para la tabla request_ids_procesados (D-b).
    IDEMPOTENCY_TTL_SECONDS: int = 86_400


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
