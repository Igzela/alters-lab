# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────┐
│              Frontend (Next.js)          │
│         TypeScript + Tailwind + shadcn  │
└──────────────────┬──────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────┐
│              Backend (FastAPI)           │
│            Python + Pydantic v2          │
├─────────────────────────────────────────┤
│  Services:                              │
│  - Project Service                      │
│  - Rubric Service                       │
│  - Script Service                       │
│  - Scoring Service                      │
│  - Prediction Service                   │
│  - Publish Service                      │
│  - Retro Service                        │
│  - Calibration Service                  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│           Data Layer (SQLite)            │
│            SQLAlchemy + Alembic          │
└─────────────────────────────────────────┘
```

## Module Breakdown

| Module | Responsibility |
|--------|---------------|
| Project Service | Manage content projects |
| Rubric Service | CRUD rubrics, version management |
| Script Service | Manage content scripts |
| Scoring Service | Score scripts against rubrics |
| Prediction Service | Create immutable blind predictions |
| Publish Service | Track content publication |
| Retro Service | Record post-publication analysis |
| Calibration Service | Generate calibration signals from retro data |

## Data Flow

1. Creator creates a project and rubric
2. Creator writes a script
3. Script is scored against current rubric
4. Blind prediction is created (immutable)
5. Content is published
6. After T+3 days, retro is recorded
7. Calibration signals are generated
8. Human reviews signals and evolves rubric
