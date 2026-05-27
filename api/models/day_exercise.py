"""Modèle ORM : association ordonnée entre un jour de séance et un exercice."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.exercise import Exercise
    from models.workout_day import WorkoutDay


class DayExercise(Base):
    """Exercice rattaché à un jour de séance, avec sa position dans la liste."""

    __tablename__ = "day_exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workout_day_id: Mapped[int] = mapped_column(
        ForeignKey("workout_days.id", ondelete="CASCADE"),
        index=True,
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), index=True)
    position: Mapped[int] = mapped_column(Integer(), default=0, server_default="0", nullable=False)

    workout_day: Mapped[WorkoutDay] = relationship(back_populates="day_exercises")
    exercise: Mapped[Exercise] = relationship()
