"""Modèle ORM Exercice (catalogue + exercices personnalisés)."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.muscle_group import MuscleGroup


class Exercise(Base):
    """Exercice de musculation (catalogue partagé ou personnalisé par utilisateur)."""

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(96), unique=True, index=True)
    name_fr: Mapped[str] = mapped_column(String(120))
    muscle_group_id: Mapped[int] = mapped_column(ForeignKey("muscle_groups.id"), index=True)
    #: Type de matériel : machine | barbell | dumbbell | cable | bodyweight | other.
    equipment: Mapped[str] = mapped_column(String(32), default="machine", server_default="machine")
    #: URL publique Supabase (catalogue ou upload communautaire).
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    #: ``None`` pour le catalogue partagé et les exercices communautaires.
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    #: Auteur d'un exercice communautaire (``owner_user_id`` reste ``None`` pour le partage global).
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
    )

    muscle_group: Mapped[MuscleGroup] = relationship(back_populates="exercises")
