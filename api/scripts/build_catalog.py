"""Génère ``seeders/data/exercises_catalog.json`` — catalogue musculation complet.

Sources fusionnées (par priorité d'image) :
1. **Everkinetic** (~293) — illustrations anatomiques 2 phases (style cible utilisateur).
2. **wger** (~845, dont ~256 avec images PNG hébergées) — complément + traductions FR partielles.
3. **free-exercise-db** (~873) — exercices machine / barre / haltères / poulie / poids du corps.

Usage : ``python scripts/build_catalog.py`` puis ``python scripts/fetch_exercise_images.py``.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from typing import TypedDict

_ROOT = Path(__file__).resolve().parent.parent
_CATALOG_PATH = _ROOT / "seeders" / "data" / "exercises_catalog.json"
_FREE_DB_CACHE = _ROOT / "seeders" / "data" / "free_exercise_db.json"

_EVERKINETIC_URL = "https://raw.githubusercontent.com/everkinetic/data/main/exercises.json"
_FREE_DB_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
_WGER_INFO_URL = "https://wger.de/api/v2/exerciseinfo/?language=2&limit=100"

MUSCLE_GROUPS: list[dict[str, object]] = [
    {"slug": "pectoraux", "name_fr": "Pectoraux", "icon": "/muscle-groups/pectoraux.svg", "sort_order": 1},
    {"slug": "dos", "name_fr": "Dos", "icon": "/muscle-groups/dos.svg", "sort_order": 2},
    {"slug": "epaules", "name_fr": "Épaules", "icon": "/muscle-groups/epaules.svg", "sort_order": 3},
    {"slug": "biceps", "name_fr": "Biceps", "icon": "/muscle-groups/biceps.svg", "sort_order": 4},
    {"slug": "triceps", "name_fr": "Triceps", "icon": "/muscle-groups/triceps.svg", "sort_order": 5},
    {"slug": "jambes", "name_fr": "Jambes (Quadriceps)", "icon": "/muscle-groups/jambes.svg", "sort_order": 6},
    {
        "slug": "ischios-fessiers",
        "name_fr": "Ischios & Fessiers",
        "icon": "/muscle-groups/ischios-fessiers.svg",
        "sort_order": 7,
    },
    {"slug": "mollets", "name_fr": "Mollets", "icon": "/muscle-groups/mollets.svg", "sort_order": 8},
    {"slug": "abdominaux", "name_fr": "Abdominaux", "icon": "/muscle-groups/abdominaux.svg", "sort_order": 9},
]

# Catégories wger pertinentes pour la musculation en salle.
_WGER_GYM_CATEGORY_IDS: set[int] = {8, 9, 10, 11, 12, 13, 14}

# Traductions FR manuelles (noms de salle les plus courants).
_FR_OVERRIDES: dict[str, str] = {
    "bench press": "Développé couché",
    "incline bench press": "Développé incliné",
    "decline bench press": "Développé décliné",
    "barbell bench press - medium grip": "Développé couché (barre)",
    "butterfly": "Pec fly (machine)",
    "pec fly": "Pec fly (machine)",
    "machine fly": "Pec fly (machine)",
    "lat pulldown": "Tirage vertical",
    "seated cable rows": "Tirage horizontal (poulie)",
    "barbell curl": "Curl barre",
    "dumbbell bicep curl": "Curl haltères",
    "triceps pushdown": "Extension triceps à la poulie",
    "leg press": "Presse à cuisses",
    "leg extensions": "Leg extension",
    "lying leg curls": "Leg curl allongé",
    "barbell squat": "Squat barre",
    "barbell full squat": "Squat barre",
    "romanian deadlift": "Soulevé de terre roumain",
    "barbell deadlift": "Soulevé de terre",
    "pullups": "Tractions",
    "pushups": "Pompes",
    "front dumbbell raise": "Élévations frontales",
    "side lateral raise": "Élévations latérales",
    "hammer curls": "Curl marteau",
    "crunches": "Crunch",
    "standing calf raises": "Mollets debout (machine)",
}


class _CatalogExercise(TypedDict, total=False):
    slug: str
    name_fr: str
    muscle_group: str
    equipment: str
    en: str
    image: str | None
    image_url: str | None
    everkinetic_id_num: str | None
    image_ext: str


def _fetch_json(url: str) -> object:
    """Télécharge et parse une ressource JSON distante.

    @param url - URL HTTP(S).
    @returns Le JSON décodé.
    """
    with urllib.request.urlopen(url, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_paginated(url: str) -> list[dict[str, object]]:
    """Récupère toutes les pages d'une collection wger.

    @param url - URL initiale de la collection.
    @returns La liste fusionnée des ``results``.
    """
    items: list[dict[str, object]] = []
    next_url: str | None = url
    while next_url is not None:
        data = _fetch_json(next_url)
        if not isinstance(data, dict):
            break
        batch = data.get("results")
        if isinstance(batch, list):
            items.extend(batch)
        next_url = data.get("next") if isinstance(data.get("next"), str) else None
    return items


def _normalize(value: str) -> str:
    """Normalise un libellé pour la déduplication.

    @param value - Chaîne source.
    @returns Forme minuscule alphanumérique.
    """
    return re.sub(r"[^a-z0-9]", "", value.lower())


def slugify(value: str) -> str:
    """Transforme un libellé en slug ASCII.

    @param value - Nom à slugifier.
    @returns Le slug.
    """
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return re.sub(r"-{2,}", "-", normalized)


def _map_everkinetic_primary(primary: str) -> str:
    """Mappe le muscle primaire Everkinetic vers un slug FitDex.

    @param primary - Muscle primaire Everkinetic.
    @returns Le slug de groupe musculaire FitDex.
    """
    key = primary.lower().strip()
    if key in {"chest"}:
        return "pectoraux"
    if key in {"lats", "middle back", "lower back", "back", "trapezius"}:
        return "dos"
    if key in {"shoulders", "lateral deltoid", "rear deltoid", "posterior deltoid"} or "deltoid" in key:
        return "epaules"
    if key == "biceps" or "biceps" in key:
        return "biceps"
    if key == "triceps" or "triceps" in key:
        return "triceps"
    if key in {"quadriceps"} or "quadriceps" in key:
        return "jambes"
    if key in {"hamstrings", "hamstring", "gluts", "glutes"}:
        return "ischios-fessiers"
    if key in {"calves"}:
        return "mollets"
    if key in {"abdominals", "lower abdominals", "obliques", "core"}:
        return "abdominaux"
    return "dos"


def _map_everkinetic_equipment(equipment: list[str]) -> str:
    """Déduit l'équipement FitDex depuis la liste Everkinetic.

    @param equipment - Liste de matériels Everkinetic.
    @returns Code équipement FitDex.
    """
    joined = " ".join(equipment).lower()
    if any(token in joined for token in ("machine", "smith", "butterfly", "press machine")):
        return "machine"
    if "cable" in joined:
        return "cable"
    if "barbell" in joined or "bar " in joined or joined.strip() == "bar":
        return "barbell"
    if "dumbbell" in joined or "dumbell" in joined:
        return "dumbbell"
    if joined.strip() in {"body", "weight"} or "parallel bars" in joined:
        return "bodyweight"
    if "bench" in joined and "barbell" not in joined:
        return "barbell"
    return "other"


def _map_free_equipment(raw: str) -> str:
    """Mappe le matériel free-exercise-db vers l'enum FitDex.

    @param raw - Valeur ``equipment`` du dataset.
    @returns Code équipement FitDex.
    """
    mapping = {
        "barbell": "barbell",
        "dumbbell": "dumbbell",
        "cable": "cable",
        "machine": "machine",
        "body only": "bodyweight",
        "e-z curl bar": "barbell",
        "kettlebells": "dumbbell",
        "bands": "cable",
        "medicine ball": "other",
        "foam roll": "other",
        "exercise ball": "other",
    }
    return mapping.get(raw.lower(), "other")


def _map_free_muscle(primary: str) -> str:
    """Mappe un muscle free-exercise-db vers FitDex.

    @param primary - Muscle primaire du dataset.
    @returns Slug groupe musculaire FitDex.
    """
    key = primary.lower()
    if key in {"chest"}:
        return "pectoraux"
    if key in {"lats", "middle back", "lower back", "traps"}:
        return "dos"
    if key in {"shoulders"}:
        return "epaules"
    if key in {"biceps", "forearms"}:
        return "biceps"
    if key in {"triceps"}:
        return "triceps"
    if key in {"quadriceps", "adductors", "abductors"}:
        return "jambes"
    if key in {"hamstrings", "glutes"}:
        return "ischios-fessiers"
    if key in {"calves"}:
        return "mollets"
    if key in {"abdominals"}:
        return "abdominaux"
    return "dos"


def _map_wger_category(category_id: int, muscles: list[dict[str, object]]) -> str:
    """Déduit le groupe musculaire FitDex depuis la catégorie / muscles wger.

    @param category_id - Identifiant catégorie wger.
    @param muscles - Muscles primaires wger.
    @returns Slug groupe FitDex.
    """
    labels = [
        str(m.get("name_en") or m.get("name") or "").lower() for m in muscles if isinstance(m, dict)
    ]
    joined = " ".join(labels)
    if category_id == 11 or "chest" in joined:
        return "pectoraux"
    if category_id == 12 or any(x in joined for x in ("lat", "back", "trap")):
        return "dos"
    if category_id == 13 or "shoulder" in joined or "deltoid" in joined:
        return "epaules"
    if category_id == 8:
        if "triceps" in joined:
            return "triceps"
        return "biceps"
    if category_id == 9:
        if any(x in joined for x in ("hamstring", "glute")):
            return "ischios-fessiers"
        return "jambes"
    if category_id == 10 or "abdom" in joined:
        return "abdominaux"
    if category_id == 14 or "calf" in joined or "calves" in joined:
        return "mollets"
    return "dos"


def _map_wger_equipment(equipment: list[dict[str, object]]) -> str:
    """Mappe l'équipement wger vers FitDex.

    @param equipment - Liste d'équipements wger.
    @returns Code équipement FitDex.
    """
    if not equipment:
        return "bodyweight"
    name = str(equipment[0].get("name", "")).lower() if isinstance(equipment[0], dict) else ""
    if "barbell" in name:
        return "barbell"
    if "dumbbell" in name:
        return "dumbbell"
    if "machine" in name or "smith" in name:
        return "machine"
    if "cable" in name or "band" in name:
        return "cable"
    if "bodyweight" in name or "none (" in name:
        return "bodyweight"
    if "kettlebell" in name:
        return "dumbbell"
    return "other"


def _french_name(en_name: str, fr_by_norm: dict[str, str]) -> str:
    """Produit un nom FR lisible pour un exercice.

    @param en_name - Nom anglais source.
    @param fr_by_norm - Traductions wger FR indexées par nom normalisé.
    @returns Le libellé français à afficher.
    """
    norm = _normalize(en_name)
    if norm in fr_by_norm:
        return fr_by_norm[norm]
    if en_name.lower() in _FR_OVERRIDES:
        return _FR_OVERRIDES[en_name.lower()]
    for key, value in _FR_OVERRIDES.items():
        if key in en_name.lower():
            return value
    return en_name


def _load_free_db() -> list[dict[str, object]]:
    """Charge le cache local free-exercise-db ou le télécharge.

    @returns Liste d'exercices du dataset.
    """
    if not _FREE_DB_CACHE.exists():
        print("Téléchargement free-exercise-db…")
        data = _fetch_json(_FREE_DB_URL)
        _FREE_DB_CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(_FREE_DB_CACHE.read_text(encoding="utf-8"))


def _upsert(
    store: dict[str, _CatalogExercise],
    entry: _CatalogExercise,
    *,
    prefer: bool = False,
) -> None:
    """Insère ou fusionne une entrée catalogue (priorité image Everkinetic > wger > free).

    @param store - Registre indexé par nom EN normalisé.
    @param entry - Nouvelle entrée.
    @param prefer - Force le remplacement si ``True``.
    """
    norm = _normalize(entry["en"])
    current = store.get(norm)
    if current is None:
        store[norm] = entry
        return
    if prefer:
        store[norm] = {**current, **entry}
        return
    # Conserver l'image la plus qualitative déjà présente.
    rank = {"everkinetic": 3, "wger": 2, "free": 1, "": 0}

    def score(item: _CatalogExercise) -> int:
        if item.get("everkinetic_id_num"):
            return rank["everkinetic"]
        if item.get("image_url"):
            return rank["wger"]
        if item.get("image"):
            return rank["free"]
        return 0

    if score(entry) > score(current):
        merged: _CatalogExercise = {**current, **entry}
        if not entry.get("name_fr"):
            merged["name_fr"] = current["name_fr"]
        store[norm] = merged


def main() -> None:
    """Construit le catalogue fusionné et l'écrit en JSON."""
    print("Chargement traductions FR wger…")
    fr_translations = _fetch_paginated("https://wger.de/api/v2/exercise-translation/?language=12&limit=100")
    fr_by_norm: dict[str, str] = {}
    for row in fr_translations:
        if row.get("language") != 12:
            continue
        name = str(row.get("name", "")).strip()
        if name:
            fr_by_norm[_normalize(name)] = name

    store: dict[str, _CatalogExercise] = {}
    seen_slugs: set[str] = set()

    def unique_slug(base: str) -> str:
        slug = slugify(base)
        candidate = slug
        suffix = 2
        while candidate in seen_slugs:
            candidate = f"{slug}-{suffix}"
            suffix += 1
        seen_slugs.add(candidate)
        return candidate

    # ----- 1. Everkinetic (images anatomiques 2 phases) -----
    print("Import Everkinetic…")
    everkinetic = _fetch_json(_EVERKINETIC_URL)
    if not isinstance(everkinetic, list):
        everkinetic = []
    for raw in everkinetic:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title") or raw.get("name") or "").strip()
        if not title:
            continue
        id_num = str(raw.get("id_num") or "").strip()
        primary = str(raw.get("primary") or "")
        equipment_raw = raw.get("equipment")
        equipment_list = equipment_raw if isinstance(equipment_raw, list) else []
        slug = unique_slug(title)
        entry: _CatalogExercise = {
            "slug": slug,
            "name_fr": _french_name(title, fr_by_norm),
            "muscle_group": _map_everkinetic_primary(primary),
            "equipment": _map_everkinetic_equipment([str(e) for e in equipment_list]),
            "en": title,
            "image": None,
            "image_url": None,
            "everkinetic_id_num": id_num or None,
            "image_ext": "jpg",
        }
        _upsert(store, entry, prefer=True)

    everk_count = sum(1 for e in store.values() if e.get("everkinetic_id_num"))
    print(f"  -> {everk_count} exercices Everkinetic")

    # ----- 2. wger exerciseinfo (salle + images PNG) -----
    print("Import wger exerciseinfo…")
    wger_infos = _fetch_paginated(_WGER_INFO_URL)
    wger_added = 0
    for info in wger_infos:
        if not isinstance(info, dict):
            continue
        category = info.get("category")
        if not isinstance(category, dict):
            continue
        category_id = int(category.get("id", 0))
        if category_id not in _WGER_GYM_CATEGORY_IDS:
            continue
        translations = info.get("translations")
        if not isinstance(translations, list) or not translations:
            continue
        en_name = str(translations[0].get("name", "")).strip()
        if not en_name:
            continue
        images = info.get("images")
        image_url: str | None = None
        if isinstance(images, list) and images:
            first = images[0]
            if isinstance(first, dict):
                image_url = str(first.get("image") or "") or None
        muscles = info.get("muscles") if isinstance(info.get("muscles"), list) else []
        equipment = info.get("equipment") if isinstance(info.get("equipment"), list) else []
        slug = unique_slug(en_name)
        entry = {
            "slug": slug,
            "name_fr": _french_name(en_name, fr_by_norm),
            "muscle_group": _map_wger_category(category_id, muscles),
            "equipment": _map_wger_equipment(equipment),
            "en": en_name,
            "image": None,
            "image_url": image_url,
            "everkinetic_id_num": None,
            "image_ext": "png" if image_url else "jpg",
        }
        before = len(store)
        _upsert(store, entry)
        if _normalize(en_name) not in {_normalize(e["en"]) for e in list(store.values())[:before]}:
            wger_added += 1
    print(f"  -> {len(store)} entrées après wger (+{wger_added} nouveaux)")

    # ----- 3. free-exercise-db (volume maximal machine + poids libres) -----
    print("Import free-exercise-db…")
    free_db = _load_free_db()
    gym_equipment = {
        "barbell",
        "dumbbell",
        "cable",
        "machine",
        "body only",
        "e-z curl bar",
        "kettlebells",
        "bands",
    }
    free_added = 0
    for raw in free_db:
        if not isinstance(raw, dict):
            continue
        equipment = str(raw.get("equipment") or "")
        if equipment.lower() not in gym_equipment:
            continue
        en_name = str(raw.get("name") or "").strip()
        if not en_name:
            continue
        primary = str(raw.get("primaryMuscles", [""])[0] if raw.get("primaryMuscles") else "")
        images = raw.get("images")
        image_path = images[0] if isinstance(images, list) and images else None
        norm = _normalize(en_name)
        if norm in store and (store[norm].get("everkinetic_id_num") or store[norm].get("image_url")):
            continue
        slug = unique_slug(en_name)
        entry = {
            "slug": slug,
            "name_fr": _french_name(en_name, fr_by_norm),
            "muscle_group": _map_free_muscle(primary),
            "equipment": _map_free_equipment(equipment),
            "en": en_name,
            "image": str(image_path) if image_path else None,
            "image_url": None,
            "everkinetic_id_num": None,
            "image_ext": "jpg",
        }
        before_len = len(store)
        _upsert(store, entry)
        if len(store) > before_len:
            free_added += 1
    print(f"  -> {free_added} exercices ajoutés depuis free-exercise-db")

    # Ne garder que les exercices avec au moins une source d'image (évite les entrées vides dans l'app).
    exercises = sorted(
        (
            e
            for e in store.values()
            if e.get("everkinetic_id_num") or e.get("image_url") or e.get("image")
        ),
        key=lambda item: (item["muscle_group"], item["name_fr"]),
    )
    catalog = {"muscle_groups": MUSCLE_GROUPS, "exercises": exercises}
    _CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    per_group: dict[str, int] = {}
    with_everk = 0
    with_wger_img = 0
    with_free_img = 0
    for ex in exercises:
        per_group[str(ex["muscle_group"])] = per_group.get(str(ex["muscle_group"]), 0) + 1
        if ex.get("everkinetic_id_num"):
            with_everk += 1
        elif ex.get("image_url"):
            with_wger_img += 1
        elif ex.get("image"):
            with_free_img += 1

    print(f"\nOK {len(exercises)} exercices -> {_CATALOG_PATH.name}")
    print(f"  Images Everkinetic (2 phases) : {with_everk}")
    print(f"  Images wger (anatomiques PNG) : {with_wger_img}")
    print(f"  Images free-exercise-db       : {with_free_img}")
    for grp in MUSCLE_GROUPS:
        slug = str(grp["slug"])
        print(f"  - {slug}: {per_group.get(slug, 0)}")


if __name__ == "__main__":
    main()
