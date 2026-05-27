"""Utilitaires de slugification."""

from __future__ import annotations

import re
import unicodedata


def slugify(value: str) -> str:
    """Transforme un libellé en slug ASCII.

    @param value - Nom à slugifier.
    @returns Le slug.
    """
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return re.sub(r"-{2,}", "-", normalized)
