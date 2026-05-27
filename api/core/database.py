"""Engine SQLAlchemy et factory de session."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import get_settings
from models import (  # noqa: F401  (import pour l'enregistrement des mappers)
    Base,
    DayExercise,
    Exercise,
    MuscleGroup,
    SetLog,
    User,
    WorkoutDay,
    WorkoutSession,
)

_settings = get_settings()
engine = create_engine(
    _settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI : fournit une session DB et la ferme après la requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
