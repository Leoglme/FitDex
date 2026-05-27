"""Modèle ORM Groupe musculaire (catégorie d'exercices)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.exercise import Exercise


class MuscleGroup(Base):
    """Catégorie musculaire (ex : Pectoraux, Dos, Triceps)."""

    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name_fr: Mapped[str] = mapped_column(String(80))
    #: Emoji ou nom d'icône pour l'affichage front.
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer(), default=0, server_default="0", nullable=False)

    exercises: Mapped[list[Exercise]] = relationship(back_populates="muscle_group")
