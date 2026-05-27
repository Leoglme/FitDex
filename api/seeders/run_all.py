"""Exécute tous les seeders (catalogue + compte admin)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> None:
    """Charge l'environnement puis lance les seeders dans l'ordre."""
    try:
        from dotenv import load_dotenv

        load_dotenv(_ROOT / ".env")
    except ImportError:
        pass

    from core.database import SessionLocal
    from seeders.catalog_seeder import seed_catalog
    from seeders.user_seeder import seed_admin_user

    db = SessionLocal()
    try:
        seed_catalog(db)
        seed_admin_user(db)
        print("Seeders terminés.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
