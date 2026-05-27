"""Routes des jours de séance : création, renommage, gestion des exercices."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func

from core.deps import CurrentUser, DbSession
from models.day_exercise import DayExercise
from models.exercise import Exercise
from models.workout_day import WorkoutDay
from schemas.workout_days import (
    DayExerciseAdd,
    WorkoutDayCreate,
    WorkoutDayPublic,
    WorkoutDayUpdate,
)

router = APIRouter(prefix="/workout-days", tags=["workout-days"])


def _get_owned_day(db: DbSession, user: CurrentUser, day_id: int) -> WorkoutDay:
    """Récupère un jour de séance appartenant à l'utilisateur, ou lève 404.

    @param db - Session DB.
    @param user - Utilisateur courant.
    @param day_id - Identifiant du jour.
    @returns Le jour de séance possédé par l'utilisateur.
    @throws HTTPException - 404 si introuvable ou non possédé.
    """
    day = db.get(WorkoutDay, day_id)
    if day is None or day.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jour de séance introuvable")
    return day


@router.get("", response_model=list[WorkoutDayPublic])
def list_days(db: DbSession, user: CurrentUser) -> list[WorkoutDay]:
    """Liste les jours de séance de l'utilisateur, ordonnés.

    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns Les jours de séance triés par position.
    """
    return (
        db.query(WorkoutDay)
        .filter(WorkoutDay.user_id == user.id)
        .order_by(WorkoutDay.position.asc(), WorkoutDay.id.asc())
        .all()
    )


@router.post("", response_model=WorkoutDayPublic, status_code=status.HTTP_201_CREATED)
def create_day(body: WorkoutDayCreate, db: DbSession, user: CurrentUser) -> WorkoutDay:
    """Crée un jour de séance ; nom par défaut "Jour N" si non fourni.

    @param body - Nom facultatif du jour.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns Le jour de séance créé.
    """
    count = db.query(func.count(WorkoutDay.id)).filter(WorkoutDay.user_id == user.id).scalar() or 0
    day = WorkoutDay(
        user_id=user.id,
        name=(body.name or f"Jour {count + 1}").strip(),
        position=count,
    )
    db.add(day)
    db.commit()
    db.refresh(day)
    return day


@router.patch("/{day_id}", response_model=WorkoutDayPublic)
def update_day(day_id: int, body: WorkoutDayUpdate, db: DbSession, user: CurrentUser) -> WorkoutDay:
    """Renomme et/ou repositionne un jour de séance.

    @param day_id - Identifiant du jour.
    @param body - Nouveau nom et/ou position.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns Le jour mis à jour.
    """
    day = _get_owned_day(db, user, day_id)
    if body.name is not None:
        day.name = body.name.strip()
    if body.position is not None:
        day.position = body.position
    db.commit()
    db.refresh(day)
    return day


@router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_day(day_id: int, db: DbSession, user: CurrentUser) -> None:
    """Supprime un jour de séance et ses exercices associés.

    @param day_id - Identifiant du jour.
    @param db - Session DB.
    @param user - Utilisateur courant.
    """
    day = _get_owned_day(db, user, day_id)
    db.delete(day)
    db.commit()


@router.post("/{day_id}/exercises", response_model=WorkoutDayPublic, status_code=status.HTTP_201_CREATED)
def add_exercise(day_id: int, body: DayExerciseAdd, db: DbSession, user: CurrentUser) -> WorkoutDay:
    """Ajoute un exercice à un jour de séance (en fin de liste).

    @param day_id - Identifiant du jour.
    @param body - Identifiant de l'exercice à ajouter.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns Le jour mis à jour avec ses exercices.
    @throws HTTPException - 404 si l'exercice n'existe pas.
    """
    day = _get_owned_day(db, user, day_id)
    if db.get(Exercise, body.exercise_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercice introuvable")
    next_position = len(day.day_exercises)
    db.add(DayExercise(workout_day_id=day.id, exercise_id=body.exercise_id, position=next_position))
    db.commit()
    db.refresh(day)
    return day


@router.delete("/{day_id}/exercises/{day_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_exercise(day_id: int, day_exercise_id: int, db: DbSession, user: CurrentUser) -> None:
    """Retire un exercice d'un jour de séance.

    @param day_id - Identifiant du jour.
    @param day_exercise_id - Identifiant de l'association jour/exercice.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @throws HTTPException - 404 si l'association n'appartient pas au jour.
    """
    day = _get_owned_day(db, user, day_id)
    link = db.get(DayExercise, day_exercise_id)
    if link is None or link.workout_day_id != day.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercice du jour introuvable")
    db.delete(link)
    db.commit()
