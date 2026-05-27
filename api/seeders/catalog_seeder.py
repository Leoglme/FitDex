"""Seeder du catalogue : groupes musculaires et exercices (idempotent par slug)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from sqlalchemy.orm import Session

from models.exercise import Exercise
from models.muscle_group import MuscleGroup

_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "exercises_catalog.json"


class _MuscleGroupRow(TypedDict):
    slug: str
    name_fr: str
    icon: str
    sort_order: int


class _ExerciseRow(TypedDict, total=False):
    slug: str
    name_fr: str
    muscle_group: str
    equipment: str
    en: str
    image_ext: str


class _Catalog(TypedDict):
    muscle_groups: list[_MuscleGroupRow]
    exercises: list[_ExerciseRow]


def _load_catalog() -> _Catalog:
    """Charge le catalogue depuis le fichier JSON bundlé.

    @returns Le catalogue (groupes musculaires + exercices).
    """
    return json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))


def seed_catalog(db: Session) -> None:
    """Insère ou met à jour les groupes musculaires et exercices à partir du JSON.

    Idempotent : chaque ligne est repérée par son ``slug``. ``image_path`` pointe vers
    l'image bundlée côté web (``/exercises/<slug>.jpg``).

    @param db - Session DB.
    """
    catalog = _load_catalog()

    group_id_by_slug: dict[str, int] = {}
    for row in catalog["muscle_groups"]:
        group = db.query(MuscleGroup).filter(MuscleGroup.slug == row["slug"]).first()
        if group is None:
            group = MuscleGroup(slug=row["slug"])
            db.add(group)
        group.name_fr = row["name_fr"]
        group.icon = row.get("icon")
        group.sort_order = row["sort_order"]
        db.flush()
        group_id_by_slug[row["slug"]] = group.id

    for row in catalog["exercises"]:
        exercise = db.query(Exercise).filter(Exercise.slug == row["slug"]).first()
        if exercise is None:
            exercise = Exercise(slug=row["slug"])
            db.add(exercise)
        exercise.name_fr = row["name_fr"]
        exercise.muscle_group_id = group_id_by_slug[row["muscle_group"]]
        exercise.equipment = row["equipment"]
        ext = str(row.get("image_ext") or "jpg")
        exercise.image_path = f"/exercises/{row['slug']}.{ext}"
        exercise.owner_user_id = None

    db.commit()
