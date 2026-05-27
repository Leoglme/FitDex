"""Schémas Pydantic pour les jours de séance et leurs exercices."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from schemas.catalog import ExercisePublic


class WorkoutDayCreate(BaseModel):
    """Création d'un jour de séance (le nom est facultatif : auto "Jour N")."""

    name: str | None = Field(default=None, max_length=80)


class WorkoutDayUpdate(BaseModel):
    """Renommage / repositionnement d'un jour de séance."""

    name: str | None = Field(default=None, min_length=1, max_length=80)
    position: int | None = None


class DayExerciseAdd(BaseModel):
    """Ajout d'un exercice à un jour de séance."""

    exercise_id: int


class DayExercisePublic(BaseModel):
    """Exercice d'un jour de séance, position incluse."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    exercise: ExercisePublic


class WorkoutDayPublic(BaseModel):
    """Jour de séance avec ses exercices ordonnés."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    position: int
    day_exercises: list[DayExercisePublic]
