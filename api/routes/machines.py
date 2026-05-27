"""Routes réglages machines (Basic Fit, etc.)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from core.deps import CurrentUser, DbSession
from models.exercise import Exercise
from models.user_machine_setting import UserMachineSetting
from schemas.machines import MachineExercisePublic, MachineSettingPublic, MachineSettingUpsert

router = APIRouter(prefix="/machines", tags=["machines"])


@router.get("/exercises", response_model=list[MachineExercisePublic])
def list_machine_exercises(
    db: DbSession,
    _user: CurrentUser,
    q: str | None = Query(default=None, min_length=1, max_length=80),
) -> list[Exercise]:
    """Liste les exercices utilisant une machine (catalogue + communauté).

    @param db - Session DB.
    @param _user - Utilisateur courant.
    @param q - Recherche texte facultative.
    @returns Les exercices machine triés par nom.
    """
    query = db.query(Exercise).filter(
        Exercise.equipment == "machine",
        Exercise.owner_user_id.is_(None),
    )
    if q is not None:
        term = f"%{q.strip()}%"
        query = query.filter(Exercise.name_fr.like(term))
    return query.order_by(Exercise.name_fr.asc()).limit(200).all()


@router.get("/settings", response_model=list[MachineSettingPublic])
def list_settings(db: DbSession, user: CurrentUser) -> list[MachineSettingPublic]:
    """Liste tous les réglages machines enregistrés par l'utilisateur.

    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns Les réglages avec le nom et l'image de l'exercice.
    """
    rows = (
        db.query(UserMachineSetting, Exercise)
        .join(Exercise, Exercise.id == UserMachineSetting.exercise_id)
        .filter(UserMachineSetting.user_id == user.id)
        .order_by(Exercise.name_fr.asc())
        .all()
    )
    return [
        MachineSettingPublic(
            id=setting.id,
            exercise_id=setting.exercise_id,
            seat_level=setting.seat_level,
            grip_level=setting.grip_level,
            notes=setting.notes,
            updated_at=setting.updated_at,
            exercise_name=exercise.name_fr,
            exercise_image_path=exercise.image_path,
        )
        for setting, exercise in rows
    ]


@router.get("/settings/{exercise_id}", response_model=MachineSettingPublic | None)
def get_setting(exercise_id: int, db: DbSession, user: CurrentUser) -> MachineSettingPublic | None:
    """Récupère les réglages d'une machine pour l'utilisateur.

    @param exercise_id - Exercice machine ciblé.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns Les réglages ou ``None`` si non enregistrés.
    """
    row = (
        db.query(UserMachineSetting, Exercise)
        .join(Exercise, Exercise.id == UserMachineSetting.exercise_id)
        .filter(UserMachineSetting.user_id == user.id, UserMachineSetting.exercise_id == exercise_id)
        .first()
    )
    if row is None:
        return None
    setting, exercise = row
    return MachineSettingPublic(
        id=setting.id,
        exercise_id=setting.exercise_id,
        seat_level=setting.seat_level,
        grip_level=setting.grip_level,
        notes=setting.notes,
        updated_at=setting.updated_at,
        exercise_name=exercise.name_fr,
        exercise_image_path=exercise.image_path,
    )


@router.put("/settings/{exercise_id}", response_model=MachineSettingPublic)
def upsert_setting(
    exercise_id: int,
    body: MachineSettingUpsert,
    db: DbSession,
    user: CurrentUser,
) -> MachineSettingPublic:
    """Crée ou met à jour les réglages d'une machine.

    @param exercise_id - Exercice machine ciblé.
    @param body - Réglages à enregistrer.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns Les réglages enregistrés.
    @throws HTTPException - 404 si l'exercice est introuvable ou n'est pas une machine.
    """
    exercise = db.get(Exercise, exercise_id)
    if exercise is None or exercise.equipment != "machine":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine introuvable")

    setting = (
        db.query(UserMachineSetting)
        .filter(UserMachineSetting.user_id == user.id, UserMachineSetting.exercise_id == exercise_id)
        .first()
    )
    if setting is None:
        setting = UserMachineSetting(user_id=user.id, exercise_id=exercise_id)
        db.add(setting)

    setting.seat_level = body.seat_level
    setting.grip_level = body.grip_level
    setting.notes = body.notes
    db.commit()
    db.refresh(setting)

    return MachineSettingPublic(
        id=setting.id,
        exercise_id=setting.exercise_id,
        seat_level=setting.seat_level,
        grip_level=setting.grip_level,
        notes=setting.notes,
        updated_at=setting.updated_at,
        exercise_name=exercise.name_fr,
        exercise_image_path=exercise.image_path,
    )
