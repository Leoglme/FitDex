"""Configuration de l'application : settings d'environnement (FastAPI + infra)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Settings FastAPI et infrastructure (depuis l'environnement / ``.env``)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "mysql+pymysql://fitdex:fitdex@127.0.0.1:3306/fitdex"
    jwt_secret: str = "change-me-in-production-use-long-random-string"
    jwt_algorithm: str = "HS256"
    #: Durée de validité du token (7 jours par défaut).
    jwt_expire_minutes: int = 10080
    cors_origins: str = "*"
    #: Compte admin seedé au déploiement (facultatif).
    seed_user_email: str | None = None
    seed_user_password: str | None = None
    #: Supabase Storage (images catalogue + uploads communautaires).
    supabase_url: str | None = None
    supabase_api_key: str | None = None
    supabase_storage_bucket: str | None = None


@lru_cache
def get_settings() -> AppSettings:
    """Singleton mis en cache des settings de l'application."""
    return AppSettings()
