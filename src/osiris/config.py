"""Configuración tipada de la aplicación.

Carga valores desde variables de entorno (prefijo ``OSIRIS_``) y desde un
archivo ``.env`` opcional. El prefijo evita colisiones con variables genéricas
del entorno del host (p. ej. ``HOST``/``PORT``).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración base del backend."""

    model_config = SettingsConfigDict(
        env_prefix="OSIRIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración cargada (cacheada para inyección y testeo)."""
    return Settings()
