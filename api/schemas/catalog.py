"""Schémas Pydantic pour le catalogue (groupes musculaires + exercices)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EquipmentType = Literal["machine", "barbell", "dumbbell", "cable", "bodyweight", "other"]


class MuscleGroupPublic(BaseModel):
    """Groupe musculaire renvoyé au front."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name_fr: str
    icon: str | None
    sort_order: int


class ExercisePublic(BaseModel):
    """Exercice renvoyé au front."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name_fr: str
    muscle_group_id: int
    equipment: str
    image_path: str | None
    description: str | None
    is_custom: bool = False


class ExerciseCreate(BaseModel):
    """Création d'un exercice personnalisé."""

    name_fr: str = Field(min_length=1, max_length=120)
    muscle_group_id: int
    equipment: EquipmentType = "machine"
    description: str | None = None


class ExerciseUpdate(BaseModel):
    """Mise à jour d'un exercice personnalisé."""

    name_fr: str | None = Field(default=None, min_length=1, max_length=120)
    muscle_group_id: int | None = None
    equipment: EquipmentType | None = None
    description: str | None = None
