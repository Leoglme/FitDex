"""Upload d'images vers Supabase Storage (clé service côté API uniquement)."""

from __future__ import annotations

import asyncio
import mimetypes
import uuid
from pathlib import Path
from typing import Any

try:
    from supabase import Client, create_client
except ImportError as _supabase_import_error:  # pragma: no cover
    Client = Any  # type: ignore[misc, assignment]
    create_client = None  # type: ignore[assignment, misc]
    _SUPABASE_IMPORT_ERROR = _supabase_import_error
else:
    _SUPABASE_IMPORT_ERROR = None

from config import AppSettings, get_settings

CATALOG_PREFIX = "exercises/catalog"
USER_PREFIX = "exercises/users"

_client: Client | None = None


def is_configured(settings: AppSettings | None = None) -> bool:
    """True si URL, clé API (service role) et bucket sont renseignés."""
    if create_client is None:
        return False
    s = settings or get_settings()
    return bool(
        (s.supabase_url or "").strip()
        and (s.supabase_api_key or "").strip()
        and (s.supabase_storage_bucket or "").strip(),
    )


def require_configured(settings: AppSettings | None = None) -> None:
    """Lève une erreur si Supabase Storage n'est pas configuré.

    @raises RuntimeError - Variables d'environnement manquantes.
    """
    if not is_configured(settings):
        raise RuntimeError(
            "Supabase Storage requis : renseignez SUPABASE_URL, SUPABASE_API_KEY et "
            "SUPABASE_STORAGE_BUCKET dans api/.env (local et production).",
        )


def _get_client() -> Client:
    global _client
    if create_client is None:
        raise RuntimeError(
            "Le package Python `supabase` est absent. Installez-le avec "
            "`pip install 'supabase>=2'` ou reconstruisez le venv.",
        ) from _SUPABASE_IMPORT_ERROR
    if _client is not None:
        return _client
    s = get_settings()
    url = (s.supabase_url or "").strip()
    key = (s.supabase_api_key or "").strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL ou SUPABASE_API_KEY manquant")
    _client = create_client(url, key)
    return _client


def _bucket_name() -> str:
    bucket = (get_settings().supabase_storage_bucket or "").strip()
    if not bucket:
        raise RuntimeError("SUPABASE_STORAGE_BUCKET manquant")
    return bucket


def _guess_content_type(filename: str | None, fallback_ext: str) -> str:
    name = filename or f"x{fallback_ext}"
    guessed, _ = mimetypes.guess_type(name)
    if guessed:
        return guessed
    ext = fallback_ext.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    return "application/octet-stream"


def catalog_object_path(slug: str, ext: str) -> str:
    """Chemin objet Storage pour une image de catalogue.

    @param slug - Slug exercice.
    @param ext - Extension sans point (ex: ``jpg``).
    @returns Chemin relatif dans le bucket.
    """
    normalized = ext.lstrip(".")
    return f"{CATALOG_PREFIX}/{slug}.{normalized}"


def user_object_path(user_id: int, original_filename: str | None) -> str:
    """Chemin objet Storage pour un upload communautaire.

    @param user_id - Auteur.
    @param original_filename - Nom d'origine (pour l'extension).
    @returns Chemin relatif dans le bucket.
    """
    ext = Path(original_filename or "img").suffix or ".jpg"
    if not ext.startswith("."):
        ext = f".{ext}"
    return f"{USER_PREFIX}/{user_id}/{uuid.uuid4().hex}{ext}"


def public_url_for_object(object_path: str) -> str:
    """Construit l'URL publique HTTPS d'un objet déjà présent dans le bucket.

    @param object_path - Chemin dans le bucket.
    @returns URL affichable côté client.
    """
    client = _get_client()
    bucket = _bucket_name()
    url = client.storage.from_(bucket).get_public_url(object_path)
    if not url or not str(url).startswith("http"):
        raise RuntimeError(f"URL publique Supabase invalide : {url!r}")
    return str(url)


def catalog_public_url(slug: str, ext: str) -> str:
    """URL publique d'une image catalogue (objet supposé existant).

    @param slug - Slug exercice.
    @param ext - Extension sans point.
    @returns URL HTTPS.
    """
    return public_url_for_object(catalog_object_path(slug, ext))


def list_catalog_filenames() -> set[str]:
    """Liste les noms de fichiers déjà présents sous ``exercises/catalog/``.

    @returns Ensemble de noms (ex: ``developpe-couche.jpg``).
    """
    client = _get_client()
    bucket = _bucket_name()
    names: set[str] = set()
    offset = 0
    page_size = 1000
    while True:
        batch = client.storage.from_(bucket).list(
            CATALOG_PREFIX,
            {"limit": page_size, "offset": offset},
        )
        if not batch:
            break
        for item in batch:
            name = item.get("name") if isinstance(item, dict) else None
            if name and not str(name).endswith("/"):
                names.add(str(name))
        if len(batch) < page_size:
            break
        offset += page_size
    return names


def upload_bytes_sync(
    *,
    object_path: str,
    data: bytes,
    content_type: str | None = None,
    original_filename: str | None = None,
) -> str:
    """Upload des octets vers le bucket et retourne l'URL publique.

    @param object_path - Chemin cible dans le bucket.
    @param data - Contenu binaire.
    @param content_type - Type MIME (deviné si absent).
    @param original_filename - Nom source pour deviner le MIME.
    @returns URL publique HTTPS.
    """
    if not data:
        raise ValueError("payload image vide")
    ext = Path(object_path).suffix or ".jpg"
    mime = content_type or _guess_content_type(original_filename, ext)
    file_options = {"content-type": mime, "upsert": "true"}

    client = _get_client()
    bucket = _bucket_name()
    client.storage.from_(bucket).upload(object_path, data, file_options=file_options)
    return public_url_for_object(object_path)


def upload_catalog_image_sync(*, slug: str, ext: str, data: bytes) -> str:
    """Upload une image catalogue (upsert).

    @param slug - Slug exercice.
    @param ext - Extension sans point.
    @param data - Octets image.
    @returns URL publique.
    """
    path = catalog_object_path(slug, ext)
    filename = f"{slug}.{ext.lstrip('.')}"
    return upload_bytes_sync(object_path=path, data=data, original_filename=filename)


def upload_user_image_sync(*, user_id: int, data: bytes, original_filename: str | None) -> str:
    """Upload une image d'exercice communautaire.

    @param user_id - Utilisateur courant.
    @param data - Octets image.
    @param original_filename - Nom du fichier uploadé.
    @returns URL publique.
    """
    path = user_object_path(user_id, original_filename)
    return upload_bytes_sync(object_path=path, data=data, original_filename=original_filename)


async def upload_user_image(*, user_id: int, data: bytes, original_filename: str | None) -> str:
    """Wrapper async pour l'upload utilisateur."""
    return await asyncio.to_thread(
        upload_user_image_sync,
        user_id=user_id,
        data=data,
        original_filename=original_filename,
    )
