<p align="center">
  <img src="web/public/favicon.svg" alt="FitDex logo" width="96" height="96" />
</p>

<h1 align="center">FitDex</h1>

<p align="center">
  <strong>Track your strength training progress — sets, reps, and weight, exercise by exercise.</strong>
</p>

<p align="center">
  <a href="https://fit.dibodev.fr">Live app</a>
  ·
  <a href="#getting-started">Getting started</a>
  ·
  <a href="#features">Features</a>
  ·
  <a href="#tech-stack">Tech stack</a>
</p>

---

## Table of contents

- [About](#about)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [API (FastAPI)](#api-fastapi)
  - [Web (Nuxt)](#web-nuxt)
- [Exercise catalog](#exercise-catalog)
- [Code quality](#code-quality)
- [Deployment](#deployment)
- [Documentation](#documentation)

---

## About

**FitDex** is a mobile-first workout tracker built for progressive overload. Log every set with reps and weight, organize workouts by day, and follow your progress over time with charts and stats.

The project is a monorepo with a **Nuxt 4** frontend and a **FastAPI** backend. It is deployed at **[fit.dibodev.fr](https://fit.dibodev.fr)**.

---

## Features

### Workout logging

- **Guided logging tunnel** — step-by-step flow to enter sets, reps, and weight
- **Smart pre-fill** — automatically loads your last performance for each exercise (set count, reps, and weight)
- **Session tracking** — log multiple exercises in a single workout session

### Exercise management

- **1,600+ exercise catalog** — browse by muscle group with anatomical illustrations
- **Search** — find exercises quickly by name across the full catalog
- **Custom exercises** — create and edit your own exercises when something is missing

### Progress & stats

- **Per-exercise charts** — max weight, top-set reps, estimated 1RM (Epley formula), and volume
- **Volume over time** — filter by muscle group or workout day
- **Workout days** — organize exercises into reusable templates (e.g. “Push day”, “Leg day”)

### App experience

- **PWA** — installable on mobile and desktop
- **JWT authentication** — secure per-user data

---

## Tech stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Nuxt 4, Vue 3, Nuxt UI 4, Tailwind CSS 4, Unovis, PWA |
| **Backend** | FastAPI, SQLAlchemy, Pydantic, JWT |
| **Database** | MariaDB / MySQL |
| **Tooling** | ESLint, Prettier, vue-tsc, Husky, commitlint, GitHub Actions |

---

## Project structure

```
FitDex/
├── api/                    # FastAPI backend
│   ├── routes/             # REST endpoints (auth, catalog, sessions, stats…)
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── services/           # Business logic (stats, auth…)
│   ├── migrations/         # SQL migrations
│   └── seeders/            # Database seeders (users, exercise catalog)
│
├── web/                    # Nuxt 4 frontend
│   ├── app/
│   │   ├── pages/          # Routes (sessions, stats, profile…)
│   │   ├── components/     # UI components (ExercisePicker, TunnelLogger…)
│   │   ├── composables/    # useApi, useAuth, useCatalog…
│   │   └── types/          # Shared TypeScript types
│   └── public/
│       ├── exercises/      # Exercise images (~1600+)
│       └── muscle-groups/  # Muscle group icons
│
└── .github/workflows/      # CI/CD (deploy-api, deploy-web)
```

---

## Getting started

### Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+
- **MariaDB** or MySQL

### API (FastAPI)

```sh
cd api
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env          # Set DATABASE_URL and JWT_SECRET
python migrations/run_migrations.py
python seeders/run_all.py     # Admin user + exercise catalog
python run_dev.py             # http://127.0.0.1:8010  (docs: /docs)
```

### Web (Nuxt)

```sh
cd web
npm install
cp .env.example .env            # NUXT_PUBLIC_API_BASE=http://127.0.0.1:8010
npm run dev                     # http://localhost:3000
```

Open the web app, register or log in, create a workout day, add exercises, and start logging.

---

## Exercise catalog

FitDex ships with a large exercise library built from merged open sources:

| Source | Content |
|--------|---------|
| [Everkinetic](https://github.com/everkinetic/data) | ~290 exercises with 2-phase anatomical illustrations |
| [wger](https://wger.de) | ~250 gym exercises with PNG images |
| [free-exercise-db](https://github.com/yuhonas/free-exercise-db) | ~570 barbell, dumbbell, machine, cable, and bodyweight exercises |

To rebuild the catalog locally:

```sh
cd api
pip install -r requirements.txt
python scripts/build_catalog.py              # → seeders/data/exercises_catalog.json
python scripts/fetch_exercise_images.py    # → web/public/exercises/ (network-heavy)
python scripts/fetch_muscle_group_images.py
python seeders/conditional_seed.py           # Sync database (idempotent)
```

---

## Code quality

### Frontend

```sh
cd web
npm run lint        # Prettier + ESLint + vue-tsc
npm run lint:fix    # Auto-fix where possible
```

Husky runs lint checks on pre-commit.

### Backend

- Strict typing (pyright) and class-based structure
- See [`STANDARDS_CODE_ET_ARCHITECTURE.md`](STANDARDS_CODE_ET_ARCHITECTURE.md) for full conventions

### Commits

Conventional Commits enforced via commitlint on `commit-msg`.

---

## Deployment

GitHub Actions workflows handle production deployment:

| Workflow | What it does |
|----------|--------------|
| `deploy-api.yml` | venv + systemd + nginx on VPS (migrations + seeders on deploy) |
| `deploy-web.yml` | Nitro build + PM2 + nginx |

Required secrets include: `SSH_HOST`, `SSH_PORT`, `SSH_USERNAME`, `SSH_PRIVATE_KEY`, `DEPLOY_API_DIR`, `DEPLOY_WEB_DIR`, `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, `NUXT_PUBLIC_API_BASE`, `NUXT_PUBLIC_SITE_URL`, and related env vars.

---

## Documentation

- **Architecture & coding standards** — [`STANDARDS_CODE_ET_ARCHITECTURE.md`](STANDARDS_CODE_ET_ARCHITECTURE.md)
- **API docs (local)** — [http://127.0.0.1:8010/docs](http://127.0.0.1:8010/docs) when running the backend

---

<p align="center">
  <sub>FitDex — built for consistent, measurable progress.</sub>
</p>
