"""Routes catalogue : groupes musculaires et exercices."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from core.deps import CurrentUser, DbSession
from models.exercise import Exercise
from models.muscle_group import MuscleGroup
from schemas.catalog import ExerciseCreate, ExercisePublic, ExerciseUpdate, MuscleGroupPublic
from utils.slug import slugify

router = APIRouter(prefix="/catalog", tags=["catalog"])

_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "exercises"
_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


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
        is_custom=exercise.created_by_user_id is not None,
    )


def _unique_community_slug(db: DbSession, user_id: int, name_fr: str) -> str:
    """Génère un slug unique pour un exercice communautaire.

    @param db - Session DB.
    @param user_id - Auteur de l'exercice.
    @param name_fr - Nom affiché.
    @returns Un slug unique.
    """
    base = slugify(name_fr) or "exercice"
    candidate = f"community-{user_id}-{base}"
    suffix = 2
    while db.query(Exercise.id).filter(Exercise.slug == candidate).first() is not None:
        candidate = f"community-{user_id}-{base}-{suffix}"
        suffix += 1
    return candidate


@router.get("/muscle-groups", response_model=list[MuscleGroupPublic])
def list_muscle_groups(db: DbSession, _user: CurrentUser) -> list[MuscleGroup]:
    """Liste les groupes musculaires triés pour la navigation par catégorie."""
    return (
        db.query(MuscleGroup)
        .order_by(MuscleGroup.sort_order.asc(), MuscleGroup.name_fr.asc())
        .all()
    )


@router.get("/exercises", response_model=list[ExercisePublic])
def list_exercises(
    db: DbSession,
    _user: CurrentUser,
    muscle_group_id: int | None = Query(default=None),
    equipment: str | None = Query(default=None),
    q: str | None = Query(default=None, min_length=1, max_length=80),
) -> list[ExercisePublic]:
    """Liste les exercices partagés (catalogue + communauté).

    @param db - Session DB.
    @param _user - Utilisateur courant.
    @param muscle_group_id - Filtre par groupe musculaire (facultatif).
    @param equipment - Filtre par type de matériel (facultatif).
    @param q - Recherche texte sur le nom (facultatif).
    @returns Les exercices correspondants, triés par nom.
    """
    query = db.query(Exercise).filter(Exercise.owner_user_id.is_(None))
    if muscle_group_id is not None:
        query = query.filter(Exercise.muscle_group_id == muscle_group_id)
    if equipment is not None:
        query = query.filter(Exercise.equipment == equipment)
    if q is not None:
        term = f"%{q.strip()}%"
        query = query.filter(Exercise.name_fr.like(term))
    exercises = query.order_by(Exercise.name_fr.asc()).limit(100).all()
    return [_exercise_public(exercise) for exercise in exercises]


@router.post("/exercises", response_model=ExercisePublic, status_code=status.HTTP_201_CREATED)
def create_exercise(body: ExerciseCreate, db: DbSession, user: CurrentUser) -> ExercisePublic:
    """Crée un exercice communautaire visible par tous les utilisateurs."""
    if db.get(MuscleGroup, body.muscle_group_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")

    exercise = Exercise(
        slug=_unique_community_slug(db, user.id, body.name_fr),
        name_fr=body.name_fr.strip(),
        muscle_group_id=body.muscle_group_id,
        equipment=body.equipment,
        description=body.description,
        image_path=body.image_path,
        owner_user_id=None,
        created_by_user_id=user.id,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return _exercise_public(exercise)


@router.post("/exercises/upload-image")
async def upload_exercise_image(
    _user: CurrentUser,
    file: UploadFile = File(...),
) -> dict[str, str]:
    """Upload une image d'exercice et renvoie son URL publique.

    @param _user - Utilisateur courant.
    @param file - Fichier image (JPEG, PNG, WebP).
    @returns Le chemin public de l'image.
    @throws HTTPException - 400 si le type de fichier n'est pas supporté.
    """
    if file.content_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Format image non supporté")

    ext = { "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp" }[file.content_type]
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = _UPLOAD_DIR / filename
    content = await file.read()
    dest.write_bytes(content)

    return {"image_path": f"/uploads/exercises/{filename}"}


@router.patch("/exercises/{exercise_id}", response_model=ExercisePublic)
def update_exercise(
    exercise_id: int,
    body: ExerciseUpdate,
    db: DbSession,
    user: CurrentUser,
) -> ExercisePublic:
    """Met à jour un exercice communautaire créé par l'utilisateur."""
    exercise = db.get(Exercise, exercise_id)
    if exercise is None or exercise.created_by_user_id != user.id:
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
    if body.image_path is not None:
        exercise.image_path = body.image_path

    db.commit()
    db.refresh(exercise)
    return _exercise_public(exercise)
