"""Schémas pour les réglages de machines."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class MachineExercisePublic(BaseModel):
    """Exercice machine du catalogue (pour la page réglages)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name_fr: str
    muscle_group_id: int
    image_path: str | None
    equipment: str


class MachineSettingPublic(BaseModel):
    """Réglages sauvegardés pour une machine."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    seat_level: int | None
    grip_level: int | None
    notes: str | None
    updated_at: dt.datetime
    exercise_name: str | None = None
    exercise_image_path: str | None = None


class MachineSettingUpsert(BaseModel):
    """Sauvegarde ou mise à jour des réglages d'une machine."""

    seat_level: int | None = Field(default=None, ge=1, le=9)
    grip_level: int | None = Field(default=None, ge=1, le=9)
    notes: str | None = Field(default=None, max_length=255)
