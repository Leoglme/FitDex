"""Modèle ORM Utilisateur."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.workout_day import WorkoutDay
    from models.workout_session import WorkoutSession


class User(Base):
    """Utilisateur de l'application (inscription libre)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80))
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False, server_default="0", nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
    )

    workout_days: Mapped[list[WorkoutDay]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    workout_sessions: Mapped[list[WorkoutSession]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
