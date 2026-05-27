"""Schémas Pydantic pour l'authentification."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Charge utile d'inscription."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=80)


class LoginRequest(BaseModel):
    """Charge utile de connexion."""

    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Réponse contenant le JWT d'accès."""

    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    """Représentation publique d'un utilisateur."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str
    is_admin: bool
