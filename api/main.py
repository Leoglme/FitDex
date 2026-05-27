"""Application FastAPI FitDex."""

from __future__ import annotations

import logging

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config import get_settings
from routes import auth as auth_routes
from routes import catalog as catalog_routes
from routes import machines as machines_routes
from routes import sessions as sessions_routes
from routes import stats as stats_routes
from routes import workout_days as workout_days_routes

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("fitdex")

settings = get_settings()

app = FastAPI(
    title="FitDex API",
    description="Backend de suivi de progression en musculation.",
    version="1.0.0",
)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if _origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Renvoie les erreurs de validation en 422 avec le détail des champs."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Journalise et renvoie une 500 propre pour toute exception non gérée."""
    logger.exception("Erreur non gérée sur %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc) or "Internal Server Error", "path": request.url.path},
    )


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Sonde de santé pour le monitoring / reverse proxy."""
    return {"status": "ok"}


app.include_router(auth_routes.router)
app.include_router(catalog_routes.router)
app.include_router(machines_routes.router)
app.include_router(workout_days_routes.router)
app.include_router(sessions_routes.router)
app.include_router(stats_routes.router)

_uploads = Path(__file__).resolve().parent / "uploads"
_uploads.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads), name="uploads")
