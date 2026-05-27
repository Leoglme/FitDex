"""Modèle ORM Série saisie (reps + charge) pour un exercice dans une séance."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.exercise import Exercise
    from models.workout_session import WorkoutSession


class SetLog(Base):
    """Une série : numéro de série, nombre de répétitions et charge en kg."""

    __tablename__ = "set_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), index=True)
    set_number: Mapped[int] = mapped_column(Integer())
    reps: Mapped[int] = mapped_column(Integer())
    #: Charge en kilogrammes (précision 0,25 kg suffisante).
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
    )

    session: Mapped[WorkoutSession] = relationship(back_populates="set_logs")
    exercise: Mapped[Exercise] = relationship()
