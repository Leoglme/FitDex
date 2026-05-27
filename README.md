# FitDex 🏋️

Suivi de progression en musculation : charges et répétitions par série, progression
surcharge progressive, statistiques par muscle / type de séance / exercice.

Monorepo :

- **`web/`** — Front Nuxt 4 (Nuxt UI 4 + Tailwind 4), PWA installable sur mobile et desktop.
- **`api/`** — Backend FastAPI (SQLAlchemy + MariaDB), auth JWT.

Déployé sur **fit.dibodev.fr**.

## Développement local

### API (FastAPI)

```sh
cd api
python -m venv .venv
. .venv/Scripts/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # renseigner DATABASE_URL + JWT_SECRET
python migrations/run_migrations.py
python seeders/run_all.py  # admin user + catalogue d'exercices
python run_dev.py          # http://127.0.0.1:8010  (docs : /docs)
```

### Catalogue d'exercices (~1600+, images anatomiques)

Sources fusionnées :

- [Everkinetic](https://github.com/everkinetic/data) — illustrations 2 phases (début/fin), muscles surlignés (~290).
- [wger](https://wger.de) — musculation salle + PNG anatomiques (~250 images).
- [free-exercise-db](https://github.com/yuhonas/free-exercise-db) — barre, haltères, machines, poulie, poids du corps (~570 images de repli).

```sh
cd api
pip install -r requirements.txt           # Pillow requis pour fusionner les 2 frames Everkinetic
python scripts/build_catalog.py           # ~1635 exercices -> seeders/data/exercises_catalog.json
python scripts/fetch_exercise_images.py   # web/public/exercises/<slug>.{jpg,png} (long, réseau)
python scripts/fetch_muscle_group_images.py
python seeders/conditional_seed.py        # synchronise la base (idempotent)
```

### Web (Nuxt)

```sh
cd web
npm install
cp .env.example .env       # NUXT_PUBLIC_API_BASE=http://127.0.0.1:8010
npm run dev                # http://localhost:3000
```

## Qualité de code

- Front : `npm run lint` (prettier + eslint + vue-tsc). Husky lance le lint au pre-commit.
- API : typage strict (pyright) + classes. Voir `STANDARDS_CODE_ET_ARCHITECTURE.md`.
- Commits : Conventional Commits (validés par commitlint au commit-msg).

## Déploiement

CI GitHub Actions :

- `deploy-api.yml` — venv + systemd + nginx sur le VPS (migrations + seeders au déploiement).
- `deploy-web.yml` — build Nitro + PM2 + nginx.

Secrets requis : `SSH_HOST`, `SSH_PORT`, `SSH_USERNAME`, `SSH_PRIVATE_KEY`,
`DEPLOY_API_DIR`, `DEPLOY_WEB_DIR`, `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`,
`NUXT_PUBLIC_API_BASE`, `NUXT_PUBLIC_SITE_URL`, etc.

> Le dossier `GoupixDex/` est une copie de référence temporaire (init/CI) et n'est pas
> versionné dans FitDex — il est ignoré par `.gitignore`.
