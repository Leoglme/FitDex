"""Calcul des statistiques de progression (charge, volume, 1RM estimé)."""

from __future__ import annotations

import datetime as dt
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.exercise import Exercise
from models.set_log import SetLog
from models.workout_session import WorkoutSession
from schemas.stats import ExerciseProgress, ExerciseSessionPoint, VolumePoint


def _epley_1rm(weight: Decimal, reps: int) -> Decimal:
    """Estime le 1RM via la formule d'Epley : ``poids * (1 + reps / 30)``.

    @param weight - Charge de la série (kg).
    @param reps - Répétitions de la série.
    @returns Le 1RM estimé, arrondi à 0,01 kg.
    """
    estimate = weight * (Decimal(1) + Decimal(reps) / Decimal(30))
    return estimate.quantize(Decimal("0.01"))


def exercise_progress(db: Session, user_id: int, exercise_id: int) -> ExerciseProgress:
    """Construit l'évolution d'un exercice dans le temps pour un utilisateur.

    Pour chaque séance : charge max, reps de la série la plus lourde, volume total,
    et 1RM estimé maximal (indicateur de force unifié reps ↔ charge).

    @param db - Session DB.
    @param user_id - Utilisateur courant.
    @param exercise_id - Exercice ciblé.
    @returns L'évolution de l'exercice, points triés par date croissante.
    """
    exercise = db.get(Exercise, exercise_id)
    exercise_name = exercise.name_fr if exercise is not None else f"#{exercise_id}"

    rows = db.execute(
        select(WorkoutSession.performed_at, SetLog.reps, SetLog.weight_kg)
        .join(SetLog, SetLog.session_id == WorkoutSession.id)
        .where(
            WorkoutSession.user_id == user_id,
            SetLog.exercise_id == exercise_id,
        )
        .order_by(WorkoutSession.performed_at.asc())
    ).all()

    by_day: dict[dt.date, list[tuple[int, Decimal]]] = defaultdict(list)
    for performed_at, reps, weight_kg in rows:
        by_day[performed_at.date()].append((reps, weight_kg))

    points: list[ExerciseSessionPoint] = []
    for day in sorted(by_day):
        sets = by_day[day]
        top_reps, top_weight = max(sets, key=lambda s: (s[1], s[0]))
        total_volume = sum((w * Decimal(r) for r, w in sets), Decimal(0))
        best_1rm = max(_epley_1rm(w, r) for r, w in sets)
        points.append(
            ExerciseSessionPoint(
                date=day,
                top_weight_kg=top_weight,
                top_set_reps=top_reps,
                total_volume_kg=total_volume.quantize(Decimal("0.01")),
                estimated_1rm=best_1rm,
            )
        )

    return ExerciseProgress(exercise_id=exercise_id, exercise_name=exercise_name, points=points)


def volume_over_time(
    db: Session,
    user_id: int,
    *,
    muscle_group_id: int | None = None,
    workout_day_id: int | None = None,
) -> list[VolumePoint]:
    """Agrège le volume total (kg) par jour, filtrable par muscle ou type de séance.

    @param db - Session DB.
    @param user_id - Utilisateur courant.
    @param muscle_group_id - Filtre par groupe musculaire (facultatif).
    @param workout_day_id - Filtre par type de séance (facultatif).
    @returns La liste des points de volume, triés par date croissante.
    """
    query = (
        select(WorkoutSession.performed_at, SetLog.reps, SetLog.weight_kg)
        .join(SetLog, SetLog.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user_id)
    )
    if muscle_group_id is not None:
        query = query.join(Exercise, Exercise.id == SetLog.exercise_id).where(
            Exercise.muscle_group_id == muscle_group_id
        )
    if workout_day_id is not None:
        query = query.where(WorkoutSession.workout_day_id == workout_day_id)

    rows = db.execute(query.order_by(WorkoutSession.performed_at.asc())).all()

    volume_by_day: dict[dt.date, Decimal] = defaultdict(lambda: Decimal(0))
    sets_by_day: dict[dt.date, int] = defaultdict(int)
    for performed_at, reps, weight_kg in rows:
        day = performed_at.date()
        volume_by_day[day] += weight_kg * Decimal(reps)
        sets_by_day[day] += 1

    return [
        VolumePoint(
            date=day,
            total_volume_kg=volume_by_day[day].quantize(Decimal("0.01")),
            sets_count=sets_by_day[day],
        )
        for day in sorted(volume_by_day)
    ]
