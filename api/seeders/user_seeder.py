"""Seeder du compte admin initial (depuis SEED_USER_EMAIL / SEED_USER_PASSWORD)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from config import get_settings
from services import auth_service


def seed_admin_user(db: Session) -> None:
    """Crée le compte admin défini par les variables d'environnement, s'il n'existe pas.

    Ne fait rien si ``SEED_USER_EMAIL`` / ``SEED_USER_PASSWORD`` ne sont pas renseignés
    (l'inscription publique reste possible via l'API).

    @param db - Session DB.
    """
    settings = get_settings()
    email = settings.seed_user_email
    password = settings.seed_user_password
    if not email or not password:
        return
    if auth_service.email_exists(db, email):
        return
    auth_service.create_user(
        db,
        email=email,
        password=password,
        display_name=email.split("@")[0],
        is_admin=True,
    )
