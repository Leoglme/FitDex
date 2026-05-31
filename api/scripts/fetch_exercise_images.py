"""Synchronise les images du catalogue vers Supabase Storage (local = production).

Priorité des sources (qualité visuelle) :
1. **Everkinetic** — 2 PNG fusionnés en JPEG.
2. **wger** — PNG hébergés sur wger.de.
3. **free-exercise-db** — illustration de repli.

Chemins : ``exercises/catalog/{slug}.{ext}`` — dédup via liste Storage.

Usage : ``cd api && PYTHONPATH=. python scripts/fetch_exercise_images.py``
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from io import BytesIO
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

_CATALOG_PATH = _ROOT / "seeders" / "data" / "exercises_catalog.json"

_EVERKINETIC_PNG_BASE = "https://raw.githubusercontent.com/everkinetic/data/main/dist/png/"
_FREE_INDEX_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
_FREE_IMAGE_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"


def _normalize(name: str) -> str:
    """Normalise un nom pour la correspondance."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _download(url: str) -> bytes:
    """Télécharge un fichier binaire."""
    req = urllib.request.Request(url, headers={"User-Agent": "FitDex/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _stitch_everkinetic_bytes(id_num: str) -> bytes | None:
    """Fusionne relaxation + tension Everkinetic en JPEG."""
    try:
        from PIL import Image
    except ImportError:
        url = f"{_EVERKINETIC_PNG_BASE}{id_num}-tension.png"
        return _download(url)

    start_url = f"{_EVERKINETIC_PNG_BASE}{id_num}-relaxation.png"
    end_url = f"{_EVERKINETIC_PNG_BASE}{id_num}-tension.png"
    try:
        start = Image.open(BytesIO(_download(start_url))).convert("RGB")
        end = Image.open(BytesIO(_download(end_url))).convert("RGB")
    except Exception:
        return None

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
    out = BytesIO()
    combined.save(out, format="JPEG", quality=88, optimize=True)
    return out.getvalue()


def _fetch_bytes_for_exercise(
    ex: dict,
    free_by_name: dict,
) -> tuple[bytes, str] | None:
    """Télécharge les octets image pour une entrée catalogue.

    @returns ``(data, ext_sans_point)`` ou ``None``.
    """
    slug = str(ex["slug"])
    ext = str(ex.get("image_ext") or "jpg").lstrip(".")
    id_num = ex.get("everkinetic_id_num")
    image_url = ex.get("image_url")
    image_path = ex.get("image")

    if id_num:
        data = _stitch_everkinetic_bytes(str(id_num))
        if data is not None:
            return data, "jpg"

    if image_url:
        return _download(str(image_url)), ext

    if image_path:
        path = str(image_path)
        entry = free_by_name.get(_normalize(str(ex.get("en", ""))))
        if entry is not None:
            images = entry.get("images")
            if isinstance(images, list) and images:
                path = str(images[0])
        return _download(_FREE_IMAGE_BASE + path), "jpg"

    return None


def main() -> None:
    """Upload les images manquantes vers Supabase Storage."""
    from services.supabase_storage_service import (
        CATALOG_PREFIX,
        catalog_object_path,
        list_catalog_filenames,
        require_configured,
        upload_catalog_image_sync,
    )

    require_configured()

    catalog = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))

    print("Index free-exercise-db (repli)…")
    with urllib.request.urlopen(_FREE_INDEX_URL, timeout=60) as resp:
        free_index = json.loads(resp.read().decode("utf-8"))
    free_by_name = {_normalize(str(e.get("name", ""))): e for e in free_index}

    existing = list_catalog_filenames()
    downloaded = 0
    skipped = 0
    missing: list[str] = []

    for ex in catalog["exercises"]:
        slug = str(ex["slug"])
        ext = str(ex.get("image_ext") or "jpg").lstrip(".")
        filename = f"{slug}.{ext}"
        if filename in existing:
            skipped += 1
            continue

        try:
            result = _fetch_bytes_for_exercise(ex, free_by_name)
            if result is None:
                missing.append(slug)
                continue
            data, file_ext = result
            upload_catalog_image_sync(slug=slug, ext=file_ext, data=data)
            existing.add(f"{slug}.{file_ext}")
            downloaded += 1
            print(f"  ok {catalog_object_path(slug, file_ext)}")
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{slug} ({exc})")

    print(f"\nTermine : {downloaded} ajoute(s), {skipped} deja presents -> Supabase / {CATALOG_PREFIX}")
    if missing:
        print(f"{len(missing)} sans image :", file=sys.stderr)
        for item in missing[:30]:
            print(f"  - {item}", file=sys.stderr)
        if len(missing) > 30:
            print(f"  ... et {len(missing) - 30} autres", file=sys.stderr)


if __name__ == "__main__":
    main()
