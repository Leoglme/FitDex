"""Schémas Pydantic pour la saisie des séances réalisées (tunnel de saisie)."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SetEntry(BaseModel):
    """Une série saisie pendant le tunnel : reps + charge."""

    set_number: int = Field(ge=1)
    reps: int = Field(ge=0)
    weight_kg: Decimal = Field(ge=0, max_digits=6, decimal_places=2)


class ExerciseLogCreate(BaseModel):
    """Saisie de toutes les séries d'un exercice (un passage du tunnel).

    La séance est créée à la volée si ``session_id`` est absent (première saisie du jour).
    """

    exercise_id: int
    workout_day_id: int | None = None
    session_id: int | None = None
    sets: list[SetEntry] = Field(min_length=1)


class SetLogPublic(BaseModel):
    """Série renvoyée au front."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    set_number: int
    reps: int
    weight_kg: Decimal


class SessionPublic(BaseModel):
    """Séance réalisée avec ses séries."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_day_id: int | None
    performed_at: dt.datetime
    set_logs: list[SetLogPublic]


class LastExerciseSet(BaseModel):
    """Une série de la dernière séance enregistrée pour un exercice."""

    set_number: int
    reps: int
    weight_kg: Decimal


class LastExerciseLog(BaseModel):
    """Dernière saisie complète d'un exercice (toutes les séries)."""

    performed_at: dt.datetime
    sets: list[LastExerciseSet]
