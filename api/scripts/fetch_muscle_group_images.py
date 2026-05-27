"""Télécharge les illustrations anatomiques des groupes musculaires (wger, AGPL).

Les SVG sont stockés dans ``web/public/muscle-groups/<slug>.svg`` pour un affichage
compréhensible dans le sélecteur de catégories (à la place des icônes Lucide).

Usage : ``python scripts/fetch_muscle_group_images.py``
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_OUTPUT_DIR = _ROOT.parent / "web" / "public" / "muscle-groups"

# Slug FitDex -> URL SVG principale (wger.de, domaine public / AGPL).
_MUSCLE_URLS: dict[str, str] = {
    "pectoraux": "https://wger.de/static/images/muscles/main/muscle-4.c9fa9a228bc8.svg",
    "dos": "https://wger.de/static/images/muscles/main/muscle-12.6a5de7a0e373.svg",
    "epaules": "https://wger.de/static/images/muscles/main/muscle-2.e1e1205a3202.svg",
    "biceps": "https://wger.de/static/images/muscles/main/muscle-1.8790f8a0b3b9.svg",
    "triceps": "https://wger.de/static/images/muscles/main/muscle-5.8a2b934b5486.svg",
    "jambes": "https://wger.de/static/images/muscles/main/muscle-10.b1445ea1acf6.svg",
    "ischios-fessiers": "https://wger.de/static/images/muscles/main/muscle-11.54ef31755917.svg",
    "mollets": "https://wger.de/static/images/muscles/main/muscle-7.edbd8c381b0c.svg",
    "abdominaux": "https://wger.de/static/images/muscles/main/muscle-6.592f938fa8c7.svg",
}


def _download(url: str, dest: Path) -> None:
    """Télécharge un fichier binaire vers ``dest``.

    @param url - URL source.
    @param dest - Chemin de destination.
    """
    with urllib.request.urlopen(url, timeout=30) as resp:
        dest.write_bytes(resp.read())


def main() -> None:
    """Télécharge les SVG des groupes musculaires FitDex."""
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    for slug, url in _MUSCLE_URLS.items():
        dest = _OUTPUT_DIR / f"{slug}.svg"
        if dest.exists():
            continue
        _download(url, dest)
        downloaded += 1
        print(f"  ok {slug}")

    manifest = {slug: f"/muscle-groups/{slug}.svg" for slug in _MUSCLE_URLS}
    (_OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Termine : {downloaded} SVG telecharge(s) dans {_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
