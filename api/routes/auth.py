"""Routes d'authentification : inscription, connexion, profil courant."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from core.deps import CurrentUser, DbSession
from core.security import create_access_token
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: DbSession) -> TokenResponse:
    """Inscrit un nouvel utilisateur et retourne directement un token d'accès.

    @param body - Email, mot de passe et nom affiché.
    @param db - Session DB.
    @returns Le JWT d'accès du compte créé.
    @throws HTTPException - 409 si l'email est déjà utilisé.
    """
    if auth_service.email_exists(db, body.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email déjà utilisé")
    user = auth_service.create_user(
        db,
        email=body.email,
        password=body.password,
        display_name=body.display_name,
    )
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: DbSession) -> TokenResponse:
    """Authentifie un utilisateur et retourne un token d'accès.

    @param body - Email et mot de passe.
    @param db - Session DB.
    @returns Le JWT d'accès.
    @throws HTTPException - 401 si les identifiants sont invalides.
    """
    user = auth_service.authenticate_user(db, body.email, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserPublic)
def me(user: CurrentUser) -> UserPublic:
    """Retourne le profil de l'utilisateur authentifié.

    @param user - Utilisateur courant (résolu depuis le JWT).
    @returns Le profil public.
    """
    return UserPublic.model_validate(user)
