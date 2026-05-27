"""Hachage de mot de passe et helpers JWT."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from config import get_settings

_BCRYPT_ROUNDS = 12


def hash_password(plain: str) -> str:
    """Hache un mot de passe avec bcrypt.

    @param plain - Mot de passe en clair.
    @returns Le hash bcrypt encodé en UTF-8.
    """
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Vérifie un mot de passe en clair contre un hash bcrypt.

    @param plain - Mot de passe en clair.
    @param hashed - Hash bcrypt stocké.
    @returns ``True`` si le mot de passe correspond, sinon ``False``.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, extra_claims: dict[str, Any] | None = None) -> str:
    """Crée un JWT signé.

    @param subject - Identifiant placé dans le claim ``sub``.
    @param extra_claims - Claims additionnels facultatifs.
    @returns Le token JWT encodé.
    """
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Décode et valide un JWT.

    @param token - Token JWT.
    @returns Le payload décodé.
    @throws JWTError - Si le token est invalide ou expiré.
    """
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def get_sub_from_token(token: str) -> str:
    """Retourne le claim ``sub`` d'un token valide.

    @param token - Token JWT.
    @returns La valeur du claim ``sub``.
    @throws JWTError - Si le claim ``sub`` est absent.
    """
    payload = decode_token(token)
    sub = payload.get("sub")
    if sub is None or not isinstance(sub, str):
        raise JWTError("Token sans sub")
    return sub
