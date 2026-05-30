# Architecture

## System Overview

Alters Lab is a personal future-path simulation and calibration system. It helps users explore structurally different life branches, engage in dialogue with hypothetical "alter" versions of themselves, score branches against their values, and calibrate predictions over time. All data is stored as YAML/JSON files on disk -- no database.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Pydantic v2, PyYAML |
| Frontend | React 18, TypeScript, Vite, Tailwind v4 |
| Data layer (FE) | TanStack Query (React Query) |
| Icons | Phosphor Icons |
| Fonts | Outfit (body), JetBrains Mono (code) |
| i18n | i18next with English and Chinese |
| Storage | YAML + JSON files under `alters/` directory |
| Packaging | Debian `.deb`, CLI entry point `alters-lab` |
| CI | GitHub Actions (backend tests + frontend build) |

## Project Layout

```
alters-lab/
  apps/
    api/                  # FastAPI backend
      src/alters_lab/
        api/              # 44 route modules
        services/         # 47 service modules
        schemas/          # 44 Pydantic schema modules
        cli/              # CLI entry point (launcher.py)
        main.py           # App factory, middleware, router registration
        middleware.py      # Rate limiting
        logging_config.py # Structured logging
      tests/              # pytest + httpx tests
      pyproject.toml      # Python package config
    web/                  # React frontend
      src/
        pages/            # 13 page components (12 active routes)
        components/       # 13 shared UI components
        hooks/            # useApi.ts (TanStack Query hooks)
        api.ts            # HTTP client functions
        types.ts          # TypeScript type definitions
        App.tsx           # Root component, hash routing, layout
        i18n.ts           # i18next config (en, zh)
        locales/          # en.json, zh.json
      vite.config.ts      # Dev proxy to backend
      package.json
  alters/                 # Runtime data directory
    current/              # Active user data (snapshot, branches, alts)
    sample/               # Sample data for onboarding
  docs/                   # Project documentation
  .github/workflows/      # CI pipeline
```

## Backend Architecture

### Entry Point

`apps/api/src/alters_lab/main.py` creates the FastAPI application. The lifespan context manager calls `setup_logging()` on startup and logs shutdown. The app title is "Alters Lab API" and version is 0.1.0.

### Middleware Stack

1. **CORS** -- `CORSMiddleware` with `allow_origins=["*"]`, all methods and headers. Required for local dev (Vite on :5173, API on :8000).
2. **Rate Limiting** -- Custom `RateLimitMiddleware` (per-IP sliding window, 600 requests per 60 seconds). Returns 429 with JSON error body when exceeded.

### Health Endpoint

`GET /health` returns `{"status": "ok", "service": "alters-lab-api"}`. Used by CLI doctor checks and CI.

### API Routers (44 modules)

All routers live in `apps/api/src/alters_lab/api/`. Each module defines a FastAPI `APIRouter`. Routers are registered in `main.py` via `app.include_router()`.

#### Core Pipeline

| Router | Prefix | Purpose |
|--------|--------|---------|
| `snapshot_intake` | `/snapshot-intake` | Capture user snapshots (constraints, uncertainties, anchors) |
| `branches` | `/branches` | Branch discovery and management |
| `alters` | `/alters` | Alter CRUD and listing |
| `generation_drafts` | `/generation-drafts` | Generate alter drafts via LLM |
| `draft_review` | `/draft-review` | Review and approve generated drafts |

#### Dialogue and Calibration

| Router | Prefix | Purpose |
|--------|--------|---------|
| `alter_dialogue` | `/alter-dialogue` | Facilitate user-alter conversations |
| `calibration_loop` | `/calibration-loop` | Score branches and track calibration |
| `rubric_delta` | `/rubric-delta` | Track rubric evolution across cycles |
| `weekly_review_session` | `/weekly-review` | Manage weekly review sessions |
| `weekly_review_assistant` | `/weekly-review-assistant` | AI-assisted weekly review suggestions |
| `weekly_reminder` | `/weekly-reminder` | Weekly review reminder scheduling |
| `obsidian_weekly_note` | `/obsidian-weekly-note` | Import/export weekly notes from Obsidian |

#### Promotion Pipeline

| Router | Prefix | Purpose |
|--------|--------|---------|
| `promotion_orchestration` | `/promotion-orchestration` | Orchestrate branch promotion workflow |
| `promotion_execution_gate` | `/promotion-execution-gate` | Gate checks before execution |
| `promotion_live_execution` | `/promotion-live-execution` | Execute promoted branch actions |
| `action_alignment` | `/action-alignment` | Score alignment between actions and branch |
| `self_deception_challenge` | `/self-deception-challenge` | Detect self-deception in branch selection |
| `alter_recommendation` | `/alter-recommendation` | Recommend alts to engage with |

#### Phase Closeouts

| Router | Purpose |
|--------|---------|
| `phase3_closeout` | Close out phase 3 (dialogue completion) |
| `phase4_closeout` | Close out phase 4 (calibration) |
| `phase5_closeout` | Close out phase 5 (weekly review) |
| `phase6_closeout` | Close out phase 6 (data retention/policy) |

#### Provider Integration (LLM)

| Router | Prefix | Purpose |
|--------|--------|---------|
| `provider_gateway` | `/provider-gateway` | Route requests to configured LLM provider |
| `provider_dialogue` | `/provider-dialogue` | LLM dialogue generation |
| `provider_dialogue_preview` | `/provider-dialogue-preview` | Preview LLM responses before committing |
| `provider_adapter` | `/provider-adapter` | Adapter pattern for multiple LLM backends |
| `provider_connectivity` | `/provider-connectivity` | Health checks for LLM providers |
| `provider_config` | `/provider-config` | Provider configuration management |
| `p6_provider_policy` | `/p6-provider-policy` | Provider usage policies and limits |

#### Data Management

| Router | Prefix | Purpose |
|--------|--------|---------|
| `storage_boundary` | `/storage-boundary` | Enforce storage limits and boundaries |
| `p6_data_retention` | `/p6-data-retention` | Data retention policies |
| `user_workflow` | `/user-workflow` | User workflow state tracking |
| `cycle_summary` | `/cycle-summary` | Summarize calibration cycles |
| `checkpoint_regeneration` | `/checkpoint-regeneration` | Regenerate checkpoint data |

#### Reporting and Validation

| Router | Prefix | Purpose |
|--------|--------|---------|
| `evidence_reports` | `/evidence` | Generate evidence reports for milestones |
| `archive_mechanism` | `/archive-mechanism` | Archive completed cycles |
| `behavior_validation` | `/behavior-validation` | Validate system behavior against spec |
| `pattern_review` | `/pattern-review` | Review patterns across calibration data |
| `product_surface` | `/product` | Product surface / export endpoints |
| `trend_analysis` | `/trend-analysis` | Linear extrapolation and confidence intervals from historical scores |
| `dynamic_weight` | `/dynamic-weight` | Advisory rubric dimension weights based on current state |
| `pattern_adjustment` | `/pattern-adjustment` | Forecast adjustment based on detected behavioral patterns |

#### Runtime and Infrastructure

| Router | Prefix | Purpose |
|--------|--------|---------|
| `runtime_layout` | `/runtime-layout` | Resolve filesystem layout (dev vs packaged) |
| `local_app` | `/local-app` | Serve frontend static files and manage local app |

### Service Layer

50 service modules in `apps/api/src/alters_lab/services/` implement business logic. Services are imported by API routers and handle:

- **Persistence**: `alters_persist`, `branches_persist`, `snapshot_persist`, `snapshot_sessions`, `snapshot_export`, `controlled_write`
- **Data safety**: `data_safety` (backup planning, archive creation)
- **LLM integration**: `provider_adapter`, `provider_gateway`, `provider_dialogue`, `provider_config`, `provider_connectivity`
- **Runtime**: `runtime_layout`, `p6_runtime`, `local_app`, `local_launcher`
- **Core logic**: One service per domain area, mirroring the router structure

### Schema Layer

41 Pydantic schema modules in `apps/api/src/alters_lab/schemas/` define request/response models. Each schema module typically corresponds to one API router.

### Structured Logging

`apps/api/src/alters_lab/logging_config.py` configures logging with:
- Format: `%(asctime)s %(levelname)s %(name)s %(message)s` (ISO 8601 timestamps)
- Default output: stderr
- Optional file output when `log_dir` is provided
- Third-party loggers (`uvicorn.access`, `httpcore`, `httpx`) silenced to WARNING level

### CLI

Entry point: `alters-lab` (defined in `pyproject.toml` `[project.scripts]`). Implemented in `apps/api/src/alters_lab/cli/launcher.py`.

| Command | Description |
|---------|-------------|
| `start` | Start the API server. Options: `--foreground`, `--no-open`, `--dry-run`, `--host`, `--port` |
| `stop` | Stop a running server |
| `status` | Show server status |
| `doctor` | Run diagnostics (checks server health, file permissions, etc.) |
| `open` | Open the app in a browser. Options: `--no-start`, `--dry-run` |
| `backup` | Create a backup archive. Options: `--include-logs`, `--include-secrets`, `--dry-run` |
| `load-sample` | Copy sample data from `alters/sample/` to `alters/current/`. Options: `--force` |

All commands support `--mode dev|packaged` and `--json` for machine-readable output.

## Frontend Architecture

### Routing

Hash-based routing (`#/page-name`). No router library. `App.tsx` reads `window.location.hash`, maps to a `Page` type, and conditionally renders the matching component. 12 active routes:

| Hash | Component | Purpose |
|------|-----------|---------|
| `#status` | SystemStatus | System health and overview (default) |
| `#weekly` | WeeklyReview | Weekly review session |
| `#dialogue` | AlterDialogue | Alter conversation interface |
| `#reality` | RealityScore | Reality scoring and divergence tracking |
| `#history` | CalibrationHistory | Historical calibration data |
| `#rubric` | RubricDelta | Rubric evolution over time |
| `#checkpoint` | CheckpointPlan | Checkpoint planning and regeneration |
| `#provider` | ProviderSettings | LLM provider configuration |
| `#getting-started` | GettingStarted | Onboarding flow |
| `#patterns` | PatternReview | Pattern analysis across cycles |
| `#validation` | BehaviorValidation | System behavior validation |
| `#data` | DataManagement | Data management and retention |

`P6Progress.tsx` exists in `pages/` but is not currently routed.

### Layout

- **Desktop** (>= 768px): Fixed 220px sidebar + scrollable content area (max-width 1080px)
- **Mobile** (< 768px): Full-width content + bottom tab bar navigation

### Data Layer

All API communication goes through `src/api.ts` (HTTP client functions) and `src/hooks/useApi.ts` (34 exported TanStack Query hooks). The hooks use `useQuery` for reads and `useMutation` for writes, with automatic cache invalidation on mutations.

Vite dev server proxies API paths to `http://localhost:8000` (see `vite.config.ts`).

### Component Library

13 shared components in `src/components/`:

| Component | Purpose |
|-----------|---------|
| `Badge` | Status/count badges |
| `Banner` | Alert/info banners |
| `Button` | Styled button with variants |
| `Card` | Content container |
| `ErrorBoundary` | React error boundary |
| `ErrorDisplay` | API error rendering |
| `Input` | Styled text input |
| `LoadingSpinner` | Loading indicator |
| `MobileNav` | Bottom tab bar (mobile) |
| `ProgressBar` | Progress indicator |
| `Sidebar` | Desktop navigation sidebar |
| `Skeleton` | Loading skeleton |
| `Toast` | Toast notification system (ToastProvider + useToast) |

### Internationalization

i18next with two locales (`en.json`, `zh.json`). Language persisted to `localStorage` under key `alters_lab_language`. Default language is English. Components use the `useTranslation` hook and `t()` function for all user-facing strings.

## Data Storage

All data lives under the `alters/` directory as YAML and JSON files. No database.

```
alters/
  current/
    snapshot.yaml        # Current user snapshot
    branches.yaml        # Discovered branches
    alters/              # Individual alter YAML files
    reality_trace.yaml   # Reality divergence observations
    weekly-notes/        # Obsidian weekly notes (imported)
    weekly-reviews/      # Weekly review session data
    evidence/            # Evidence reports
    calibration/         # Calibration cycle data
    config/              # Provider and runtime config
  sample/                # Sample data for new users
    snapshot.yaml
    branches.yaml
    reality_trace.yaml
    alters/
      alter_A.yaml
      alter_B.yaml
      alter_C.yaml
      alter_D.yaml
```

Key data entities (defined in `docs/data-model.md`):

- **Snapshot**: User's current state -- heaviest constraint, most unclear direction, non-negotiables
- **Branch**: Structurally distinct future path with tradeoffs
- **Alter**: Coherent version of the user on a specific branch, with values and narrative
- **RealityTrace**: Observation of how reality diverges from predicted branch
- **RealityScore**: Multi-dimensional scoring of branches against user rubric

## Packaging and Deployment

### Debian Package

Built as a `.deb` package. The `runtime_layout` module resolves paths differently for `dev` mode (local source tree) vs `packaged` mode (installed system-wide). The CLI `--mode` flag overrides auto-detection.

### Systemd Integration

Packaged mode expects systemd service files for process management. The `local_launcher` service handles start/stop/status using the appropriate mechanism for each mode.

## CI/CD

GitHub Actions pipeline (`.github/workflows/ci.yml`) triggers on push to `main` and pull requests:

| Job | Runner | Steps |
|-----|--------|-------|
| Backend Tests | ubuntu-latest | Python 3.11, `pip install -e ".[dev]"`, `pytest apps/api/tests/ -q` |
| Frontend Build | ubuntu-latest | Node 22, `npm ci`, `npm run build` |

Both jobs run in parallel. No deployment step -- the app runs locally.

## Sample Data

The `alters/sample/` directory contains pre-built sample data for new users:

- `snapshot.yaml` -- A sample user snapshot
- `branches.yaml` -- Four sample branches (A, B, C, D)
- `alters/alter_A.yaml` through `alter_D.yaml` -- Four alter profiles
- `reality_trace.yaml` -- Sample reality observations

The `load-sample` CLI command copies these into `alters/current/`. It skips files that already exist unless `--force` is passed. The GettingStarted page in the frontend guides users through this flow.
