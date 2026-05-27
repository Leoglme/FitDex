"""Modèle ORM Séance réalisée (instance d'entraînement à une date donnée)."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.set_log import SetLog
    from models.user import User


class WorkoutSession(Base):
    """Séance effectivement réalisée : regroupe les séries saisies ce jour-là."""

    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    #: Jour de séance source ; ``None`` si le jour a été supprimé depuis.
    workout_day_id: Mapped[int | None] = mapped_column(
        ForeignKey("workout_days.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    performed_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        index=True,
    )

    user: Mapped[User] = relationship(back_populates="workout_sessions")
    set_logs: Mapped[list[SetLog]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
