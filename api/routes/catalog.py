"""Routes catalogue : groupes musculaires et exercices."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from core.deps import CurrentUser, DbSession
from models.exercise import Exercise
from models.muscle_group import MuscleGroup
from schemas.catalog import ExerciseCreate, ExercisePublic, ExerciseUpdate, MuscleGroupPublic
from utils.slug import slugify

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _exercise_public(exercise: Exercise) -> ExercisePublic:
    """Sérialise un exercice ORM avec le flag ``is_custom``.

    @param exercise - Exercice ORM.
    @returns Le schéma public.
    """
    return ExercisePublic(
        id=exercise.id,
        slug=exercise.slug,
        name_fr=exercise.name_fr,
        muscle_group_id=exercise.muscle_group_id,
        equipment=exercise.equipment,
        image_path=exercise.image_path,
        description=exercise.description,
        is_custom=exercise.owner_user_id is not None,
    )


def _unique_custom_slug(db: DbSession, user_id: int, name_fr: str) -> str:
    """Génère un slug unique pour un exercice personnalisé.

    @param db - Session DB.
    @param user_id - Propriétaire de l'exercice.
    @param name_fr - Nom affiché de l'exercice.
    @returns Un slug unique.
    """
    base = slugify(name_fr) or "exercice"
    candidate = f"custom-{user_id}-{base}"
    suffix = 2
    while db.query(Exercise.id).filter(Exercise.slug == candidate).first() is not None:
        candidate = f"custom-{user_id}-{base}-{suffix}"
        suffix += 1
    return candidate


@router.get("/muscle-groups", response_model=list[MuscleGroupPublic])
def list_muscle_groups(db: DbSession, _user: CurrentUser) -> list[MuscleGroup]:
    """Liste les groupes musculaires triés pour la navigation par catégorie.

    @param db - Session DB.
    @param _user - Utilisateur courant (auth requise).
    @returns Les groupes musculaires triés par ``sort_order`` puis nom.
    """
    return (
        db.query(MuscleGroup)
        .order_by(MuscleGroup.sort_order.asc(), MuscleGroup.name_fr.asc())
        .all()
    )


@router.get("/exercises", response_model=list[ExercisePublic])
def list_exercises(
    db: DbSession,
    user: CurrentUser,
    muscle_group_id: int | None = Query(default=None),
    q: str | None = Query(default=None, min_length=1, max_length=80),
) -> list[ExercisePublic]:
    """Liste les exercices du catalogue partagé (et les exercices custom de l'utilisateur).

    @param db - Session DB.
    @param user - Utilisateur courant.
    @param muscle_group_id - Filtre par groupe musculaire (facultatif).
    @param q - Recherche texte sur le nom (facultatif).
    @returns Les exercices correspondants, triés par nom.
    """
    query = db.query(Exercise).filter(
        (Exercise.owner_user_id.is_(None)) | (Exercise.owner_user_id == user.id)
    )
    if muscle_group_id is not None:
        query = query.filter(Exercise.muscle_group_id == muscle_group_id)
    if q is not None:
        term = f"%{q.strip()}%"
        query = query.filter(Exercise.name_fr.like(term))
    exercises = query.order_by(Exercise.name_fr.asc()).limit(100).all()
    return [_exercise_public(exercise) for exercise in exercises]


@router.post("/exercises", response_model=ExercisePublic, status_code=status.HTTP_201_CREATED)
def create_exercise(body: ExerciseCreate, db: DbSession, user: CurrentUser) -> ExercisePublic:
    """Crée un exercice personnalisé pour l'utilisateur courant.

    @param body - Données de l'exercice.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns L'exercice créé.
    @throws HTTPException - 404 si le groupe musculaire est introuvable.
    """
    if db.get(MuscleGroup, body.muscle_group_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")

    exercise = Exercise(
        slug=_unique_custom_slug(db, user.id, body.name_fr),
        name_fr=body.name_fr.strip(),
        muscle_group_id=body.muscle_group_id,
        equipment=body.equipment,
        description=body.description,
        owner_user_id=user.id,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return _exercise_public(exercise)


@router.patch("/exercises/{exercise_id}", response_model=ExercisePublic)
def update_exercise(
    exercise_id: int,
    body: ExerciseUpdate,
    db: DbSession,
    user: CurrentUser,
) -> ExercisePublic:
    """Met à jour un exercice personnalisé appartenant à l'utilisateur.

    @param exercise_id - Exercice ciblé.
    @param body - Champs à modifier.
    @param db - Session DB.
    @param user - Utilisateur courant.
    @returns L'exercice mis à jour.
    @throws HTTPException - 404 si l'exercice est introuvable ou non modifiable.
    """
    exercise = db.get(Exercise, exercise_id)
    if exercise is None or exercise.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercice introuvable")

    if body.muscle_group_id is not None:
        if db.get(MuscleGroup, body.muscle_group_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
        exercise.muscle_group_id = body.muscle_group_id

    if body.name_fr is not None:
        exercise.name_fr = body.name_fr.strip()
    if body.equipment is not None:
        exercise.equipment = body.equipment
    if body.description is not None:
        exercise.description = body.description

    db.commit()
    db.refresh(exercise)
    return _exercise_public(exercise)
