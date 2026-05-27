"""Routes de saisie des séances réalisées (tunnel de saisie reps + charge)."""

from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from core.deps import CurrentUser, DbSession
from models.exercise import Exercise
from models.set_log import SetLog
from models.workout_session import WorkoutSession
from schemas.sessions import ExerciseLogCreate, LastExerciseLog, LastExerciseSet, SessionPublic

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/log-exercise", response_model=SessionPublic, status_code=status.HTTP_201_CREATED)
def log_exercise(body: ExerciseLogCreate, db: DbSession, user: CurrentUser) -> WorkoutSession:
    """Enregistre toutes les séries d'un exercice (un passage du tunnel).

    Crée la séance du jour si ``session_id`` est absent, sinon réutilise la séance
    en cours (les exercices suivants du même jour s'y rattachent).

    @param body - Exercice, jour source facultatif, séance facultative et séries.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns La séance avec l'ensemble de ses séries.
    @throws HTTPException - 404 si l'exercice ou la séance ciblée est introuvable.
    """
    if db.get(Exercise, body.exercise_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercice introuvable")

    if body.session_id is not None:
        session = db.get(WorkoutSession, body.session_id)
        if session is None or session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Séance introuvable")
    else:
        session = WorkoutSession(
            user_id=user.id,
            workout_day_id=body.workout_day_id,
            performed_at=dt.datetime.now(dt.UTC),
        )
        db.add(session)
        db.flush()

    for entry in body.sets:
        db.add(
            SetLog(
                session_id=session.id,
                exercise_id=body.exercise_id,
                set_number=entry.set_number,
                reps=entry.reps,
                weight_kg=entry.weight_kg,
            )
        )
    db.commit()
    db.refresh(session)
    return session


@router.get("/last-exercise/{exercise_id}", response_model=LastExerciseLog | None)
def last_exercise_log(exercise_id: int, db: DbSession, user: CurrentUser) -> LastExerciseLog | None:
    """Renvoie la dernière saisie complète d'un exercice (toutes les séries).

    @param exercise_id - Exercice ciblé.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns Les séries de la dernière séance contenant cet exercice, ou ``None``.
    """
    if db.get(Exercise, exercise_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercice introuvable")

    last_session_id = db.execute(
        select(WorkoutSession.id)
        .join(SetLog, SetLog.session_id == WorkoutSession.id)
        .where(
            WorkoutSession.user_id == user.id,
            SetLog.exercise_id == exercise_id,
        )
        .order_by(WorkoutSession.performed_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if last_session_id is None:
        return None

    session = db.get(WorkoutSession, last_session_id)
    if session is None:
        return None

    sets = (
        db.query(SetLog)
        .filter(SetLog.session_id == last_session_id, SetLog.exercise_id == exercise_id)
        .order_by(SetLog.set_number.asc())
        .all()
    )

    return LastExerciseLog(
        performed_at=session.performed_at,
        sets=[
            LastExerciseSet(set_number=log.set_number, reps=log.reps, weight_kg=log.weight_kg)
            for log in sets
        ],
    )


@router.get("/recent", response_model=list[SessionPublic])
def recent_sessions(db: DbSession, user: CurrentUser, limit: int = 20) -> list[WorkoutSession]:
    """Liste les dernières séances réalisées de l'utilisateur.

    @param db - Session DB.
    @param user - Utilisateur courant.
    @param limit - Nombre maximum de séances renvoyées.
    @returns Les séances récentes, les plus récentes d'abord.
    """
    return (
        db.query(WorkoutSession)
        .filter(WorkoutSession.user_id == user.id)
        .order_by(WorkoutSession.performed_at.desc())
        .limit(min(limit, 100))
        .all()
    )
