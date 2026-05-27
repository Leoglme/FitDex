"""Seed conditionnel exécuté au déploiement : ne (re)seed que ce qui manque."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> None:
    """Seed le catalogue s'il est vide et crée l'admin s'il n'existe pas encore."""
    try:
        from dotenv import load_dotenv

        load_dotenv(_ROOT / ".env")
    except ImportError:
        pass

    from core.database import SessionLocal
    from models.muscle_group import MuscleGroup
    from seeders.catalog_seeder import seed_catalog
    from seeders.user_seeder import seed_admin_user

    db = SessionLocal()
    try:
        # Idempotent : met à jour noms, images et ajoute les nouveaux exercices du JSON.
        seed_catalog(db)
        print("Catalogue synchronisé.")
        seed_admin_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
