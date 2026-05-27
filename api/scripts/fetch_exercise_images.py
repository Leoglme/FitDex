"""Télécharge les images d'exercices dans ``web/public/exercises/`` (PWA hors-ligne).

Priorité des sources (qualité visuelle) :
1. **Everkinetic** — 2 PNG (relaxation + tension) fusionnés côte à côte (style anatomique).
2. **wger** — PNG Everkinetic hébergés sur wger.de.
3. **free-exercise-db** — illustration de repli.

Usage : ``python scripts/fetch_exercise_images.py``
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from io import BytesIO
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_CATALOG_PATH = _ROOT / "seeders" / "data" / "exercises_catalog.json"
_OUTPUT_DIR = _ROOT.parent / "web" / "public" / "exercises"

_EVERKINETIC_PNG_BASE = "https://raw.githubusercontent.com/everkinetic/data/main/dist/png/"
_FREE_INDEX_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
_FREE_IMAGE_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"


def _normalize(name: str) -> str:
    """Normalise un nom pour la correspondance.

    @param name - Nom d'exercice.
    @returns Forme normalisée.
    """
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _download(url: str) -> bytes:
    """Télécharge un fichier binaire.

    @param url - URL source.
    @returns Le contenu binaire.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "FitDex/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _stitch_everkinetic(id_num: str, dest: Path) -> bool:
    """Fusionne relaxation + tension Everkinetic en une image JPEG.

    @param id_num - Identifiant Everkinetic (ex: ``0042``).
    @param dest - Fichier de sortie.
    @returns ``True`` si le téléchargement a réussi.
    """
    try:
        from PIL import Image
    except ImportError:
        # Repli : une seule frame si Pillow absent.
        url = f"{_EVERKINETIC_PNG_BASE}{id_num}-tension.png"
        dest.write_bytes(_download(url))
        return True

    start_url = f"{_EVERKINETIC_PNG_BASE}{id_num}-relaxation.png"
    end_url = f"{_EVERKINETIC_PNG_BASE}{id_num}-tension.png"
    try:
        start = Image.open(BytesIO(_download(start_url))).convert("RGB")
        end = Image.open(BytesIO(_download(end_url))).convert("RGB")
    except Exception:
        return False

    height = max(start.height, end.height)

    def resize(img: Image.Image) -> Image.Image:
        if img.height == height:
            return img
        ratio = height / img.height
        return img.resize((int(img.width * ratio), height), Image.Resampling.LANCZOS)

    start_r = resize(start)
    end_r = resize(end)
    combined = Image.new("RGB", (start_r.width + end_r.width, height), (255, 255, 255))
    combined.paste(start_r, (0, 0))
    combined.paste(end_r, (start_r.width, 0))
    combined.save(dest, format="JPEG", quality=88, optimize=True)
    return True


def main() -> None:
    """Télécharge les images du catalogue vers ``web/public/exercises/``."""
    catalog = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Index free-exercise-db (repli)…")
    with urllib.request.urlopen(_FREE_INDEX_URL, timeout=60) as resp:
        free_index = json.loads(resp.read().decode("utf-8"))
    free_by_name = {_normalize(str(e.get("name", ""))): e for e in free_index}

    downloaded = 0
    skipped = 0
    missing: list[str] = []

    for ex in catalog["exercises"]:
        slug = str(ex["slug"])
        ext = str(ex.get("image_ext") or "jpg")
        dest = _OUTPUT_DIR / f"{slug}.{ext}"
        if dest.exists():
            skipped += 1
            continue

        id_num = ex.get("everkinetic_id_num")
        image_url = ex.get("image_url")
        image_path = ex.get("image")

        try:
            if id_num:
                jpg_dest = _OUTPUT_DIR / f"{slug}.jpg"
                if _stitch_everkinetic(str(id_num), jpg_dest):
                    downloaded += 1
                    print(f"  ok [everkinetic] {slug}")
                    continue
            if image_url:
                raw = _download(str(image_url))
                dest.write_bytes(raw)
                downloaded += 1
                print(f"  ok [wger] {slug}")
                continue
            if image_path:
                path = str(image_path)
                entry = free_by_name.get(_normalize(str(ex.get("en", ""))))
                if entry is not None:
                    images = entry.get("images")
                    if isinstance(images, list) and images:
                        path = str(images[0])
                free_dest = _OUTPUT_DIR / f"{slug}.jpg"
                free_dest.write_bytes(_download(_FREE_IMAGE_BASE + path))
                downloaded += 1
                print(f"  ok [free-db] {slug}")
                continue
            missing.append(slug)
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{slug} ({exc})")

    print(f"\nTermine : {downloaded} telecharge(s), {skipped} deja presents -> {_OUTPUT_DIR}")
    if missing:
        print(f"{len(missing)} sans image :", file=sys.stderr)
        for item in missing[:30]:
            print(f"  - {item}", file=sys.stderr)
        if len(missing) > 30:
            print(f"  ... et {len(missing) - 30} autres", file=sys.stderr)


if __name__ == "__main__":
    main()
