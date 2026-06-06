# Alters Lab

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/Igzela/alters-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Igzela/alters-lab/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-1970%20backend%20%2B%2084%20frontend-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![React](https://img.shields.io/badge/react-18-61dafb)]()

**Your future is not a single path. It's a branching tree of possibilities.**

Alters Lab is a personal future path simulation and calibration system. It helps you explore structurally different life branches, engage in dialogue with hypothetical versions of yourself, and calibrate which paths actually align with your values — using both population-level evidence and your own weekly calibration data.

## Quick Start

```bash
git clone https://github.com/Igzela/alters-lab.git
cd alters-lab
docker compose up -d
# Open http://localhost:18790
```

Load sample data to explore immediately:

```bash
docker compose exec alters-lab alters-lab load-sample
```

## Manual Install

**Backend:**

```bash
git clone https://github.com/Igzela/alters-lab.git
cd alters-lab
python3 -m venv .venv && source .venv/bin/activate
pip install -e "apps/api[dev]"
```

**Frontend:**

```bash
cd apps/web
npm install
```

**Run (development mode):**

```bash
# Terminal 1 — Backend
PYTHONPATH=apps/api/src uvicorn alters_lab.main:app --port 18790

# Terminal 2 — Frontend (hot-reload)
cd apps/web && npm run dev
```

Frontend at `http://localhost:5173`, API at `http://localhost:18790`.

**Run (production mode):**

```bash
source .venv/bin/activate
alters-lab start
# Opens http://localhost:18790
```

## API Overview

The API exposes 50+ endpoints across these key areas:

| Area | Endpoints | Description |
|------|-----------|-------------|
| **Snapshot** | `POST /snapshot-intake/...` | Capture current state: constraints, directions, values |
| **Branches** | `GET/POST /branches/...` | Discover and manage 3-4 structural life branches |
| **Alters** | `GET /alters/...` | List and manage generated alter personas |
| **Dialogue** | `POST /alter-dialogue/{alter_id}/...` | Chat with an alter about their path |
| **Weekly Review** | `POST /weekly-review-session/...` | 6-step structured weekly calibration flow |
| **Calibration** | `POST /calibration-conversation/...` | LLM-guided calibration via natural conversation |
| **Behavior Metrics** | `GET/POST /behavior-metrics/...` | Weekly structured behavior indicators |
| **Forecast** | `GET /branch-forecast/...` | Route A + Route B + Adapter combined forecasts |
| **Snapshots** | `GET /forecast-snapshots/...` | Locked, immutable forecast records |
| **Evidence** | `POST /external-evidence/...` | Real-world observations that inform forecasts |
| **Evaluation** | `GET /forecast-evaluation/...` | Hit/miss tracking per domain, per source |
| **Scorecard** | `GET /calibration-scorecard/...` | Aggregate accuracy with per-source hit rates |
| **Provider** | `POST /provider-config/...` | Configure LLM provider (OpenAI-compatible) |
| **Public Priors** | `GET /public-prior/...` | Population-level baselines from NLSY97/MIDUS |

Full API docs at `http://localhost:18790/docs` (Swagger UI).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend  React 18 + TypeScript + Tailwind v4          │
│  15 pages: Dashboard, Weekly Review, Dialogue, etc.     │
├─────────────────────────────────────────────────────────┤
│  Backend  Python 3.11+ + FastAPI + Pydantic v2          │
│  50+ API routers, 55 service modules                    │
│  Route B population priors (NLSY97 + MIDUS)             │
│  Personal Prior Adapter + Pattern Detection             │
├─────────────────────────────────────────────────────────┤
│  Storage  YAML + JSON files (no database)               │
│  alters/current/   Active user data                     │
│  alters/product/   Reviews, forecasts, evidence         │
│  alters/calibration/  Rubric, scores, state             │
└─────────────────────────────────────────────────────────┘

Pipeline:
  Snapshot → Branch Discovery → Alter Generation → Dialogue → Calibration
      ↓                                                          ↓
      └──────────── Reality Score ←──── Weekly Reviews ←──────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Pydantic v2, PyYAML, uvicorn |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4 |
| Data | TanStack Query, Recharts, Phosphor Icons |
| i18n | English + Chinese |
| Storage | YAML + JSON files |
| Deployment | Docker, Debian `.deb` |
| Tests | pytest (backend), vitest (frontend) |

## Development

**Run all tests:**

```bash
# Backend (1970 tests)
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q

# Frontend (84 tests)
cd apps/web && npm run test

# Frontend build check
cd apps/web && npm run build
```

**Generate TypeScript types from OpenAPI:**

```bash
cd apps/web && npm run generate:types
```

**CLI commands:**

```bash
alters-lab start        # Start local server
alters-lab stop         # Stop local server
alters-lab status       # Show server status
alters-lab doctor       # Run health checks
alters-lab backup       # Create a data backup
alters-lab load-sample  # Load sample data for new users
```

## Key Concepts

- **Route A** — Personal evidence from your calibration data
- **Route B** — Population priors from longitudinal datasets (NLSY97, MIDUS)
- **Personal Prior Adapter** — Combines Route A + Route B + external evidence into per-domain forecasts
- **Calibration** — 4-dimension rubric: execution discipline, exploration freedom, life state match, energy level
- **No life_score** — The system never produces a single number for your life quality
- **No exact probability** — Directional forecasts only, with explicit uncertainty

## Documentation

- [User Guide](docs/USER_GUIDE.md) — Workflow walkthrough and reference
- [Provider Setup](docs/user/PROVIDER_SETUP.md) — Configure LLM providers
- [Architecture](docs/architecture.md) — Technical architecture
- [Data Model](docs/data-model.md) — Schema definitions
- [Product Spec](docs/product-spec.md) — System design and concepts

## License

[MIT](LICENSE) — Use it, modify it, distribute it. Just keep the license notice.
