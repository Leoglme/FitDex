"""Modèle ORM Jour de séance (ex : "Jour 1", renommable en "Séance dos biceps")."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.day_exercise import DayExercise
    from models.user import User


class WorkoutDay(Base):
    """Jour de séance configuré par l'utilisateur, contenant une liste d'exercices."""

    __tablename__ = "workout_days"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    position: Mapped[int] = mapped_column(Integer(), default=0, server_default="0", nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
    )

    user: Mapped[User] = relationship(back_populates="workout_days")
    day_exercises: Mapped[list[DayExercise]] = relationship(
        back_populates="workout_day",
        cascade="all, delete-orphan",
        order_by="DayExercise.position",
    )
