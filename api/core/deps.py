"""Dépendances FastAPI (auth, DB)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_sub_from_token
from models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Exige un JWT Bearer valide et retourne le ``User`` correspondant.

    @param credentials - Identifiants Bearer extraits de l'en-tête Authorization.
    @param db - Session DB.
    @returns L'utilisateur authentifié.
    @throws HTTPException - 401 si le token est absent, invalide, ou l'utilisateur introuvable.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non authentifié")
    try:
        user_id = int(get_sub_from_token(credentials.credentials))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide") from None
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
