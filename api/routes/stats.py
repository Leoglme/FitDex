"""Routes statistiques : progression par exercice, volume par muscle / type de séance."""

from __future__ import annotations

from fastapi import APIRouter, Query

from core.deps import CurrentUser, DbSession
from schemas.stats import ExerciseProgress, VolumePoint
from services import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/exercise/{exercise_id}", response_model=ExerciseProgress)
def exercise_progress(exercise_id: int, db: DbSession, user: CurrentUser) -> ExerciseProgress:
    """Évolution d'un exercice : charge, reps de la série lourde, volume et 1RM estimé.

    @param exercise_id - Exercice ciblé.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns L'évolution de l'exercice dans le temps.
    """
    return stats_service.exercise_progress(db, user.id, exercise_id)


@router.get("/volume", response_model=list[VolumePoint])
def volume(
    db: DbSession,
    user: CurrentUser,
    muscle_group_id: int | None = Query(default=None),
    workout_day_id: int | None = Query(default=None),
) -> list[VolumePoint]:
    """Volume total (kg) agrégé par jour, filtrable par muscle ou type de séance.

    @param db - Session DB.
    @param user - Utilisateur courant.
    @param muscle_group_id - Filtre par groupe musculaire (facultatif).
    @param workout_day_id - Filtre par type de séance (facultatif).
    @returns La série temporelle de volume.
    """
    return stats_service.volume_over_time(
        db,
        user.id,
        muscle_group_id=muscle_group_id,
        workout_day_id=workout_day_id,
    )
