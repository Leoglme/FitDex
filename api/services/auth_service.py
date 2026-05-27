"""Service d'authentification (inscription, connexion)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from core.security import hash_password, verify_password
from models.user import User


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Retourne l'utilisateur si email + mot de passe correspondent, sinon ``None``.

    @param db - Session DB.
    @param email - Email saisi.
    @param password - Mot de passe en clair.
    @returns L'utilisateur authentifié ou ``None``.
    """
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if user is None or not verify_password(password, user.password):
        return None
    return user


def email_exists(db: Session, email: str) -> bool:
    """Indique si un compte existe déjà pour cet email.

    @param db - Session DB.
    @param email - Email à vérifier.
    @returns ``True`` si l'email est déjà utilisé.
    """
    return db.query(User).filter(User.email == email.strip().lower()).first() is not None


def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    display_name: str,
    is_admin: bool = False,
) -> User:
    """Crée un utilisateur avec mot de passe haché.

    @param db - Session DB.
    @param email - Email (normalisé en minuscules).
    @param password - Mot de passe en clair (sera haché).
    @param display_name - Nom affiché.
    @param is_admin - Drapeau administrateur.
    @returns L'utilisateur créé et persisté.
    """
    user = User(
        email=email.strip().lower(),
        password=hash_password(password),
        display_name=display_name.strip(),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
