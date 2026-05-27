"""Schémas Pydantic pour les statistiques de progression."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pydantic import BaseModel


class ExerciseSessionPoint(BaseModel):
    """Point d'évolution d'un exercice pour une séance donnée.

    ``estimated_1rm`` (formule d'Epley) combine charge et reps en un seul indicateur
    de force, ce qui permet de suivre la progression même quand on échange reps ↔ charge.
    """

    date: dt.date
    top_weight_kg: Decimal
    top_set_reps: int
    total_volume_kg: Decimal
    estimated_1rm: Decimal


class ExerciseProgress(BaseModel):
    """Évolution complète d'un exercice dans le temps."""

    exercise_id: int
    exercise_name: str
    points: list[ExerciseSessionPoint]


class VolumePoint(BaseModel):
    """Volume total (kg) agrégé sur une date (tous exercices ou filtré)."""

    date: dt.date
    total_volume_kg: Decimal
    sets_count: int
