# Architecture

## System Overview

Alters Lab is a personal future-path simulation and calibration system. It helps users explore structurally different life branches, engage in dialogue with hypothetical "alter" versions of themselves, score branches against their values, and calibrate predictions over time. All user data is stored as YAML/JSON files on disk -- no database.

The main evidence source is the user's own data: weekly reviews, behavior metrics, explicit scores, outcome targets, and real-world observations. Optional external reference context can be used only as background context when source terms, validation, and applicability limits are clear. It must not be presented as official endorsement, a direct individual prediction, or a commercial proof point.

```
+------------------------------------------------------+
|                   Frontend (React)                    |
|  Pages + hooks + shared UI components                |
+---------------------------+--------------------------+
                            | HTTP (fetch)
                            v
+------------------------------------------------------+
|                   Backend (FastAPI)                   |
|  API routers --> services --> DataRepo               |
+---------------------------+--------------------------+
                            |
                            v
+------------------------------------------------------+
|              Data Storage (YAML/JSON files)           |
|  alters/current/ + alters/product/ + alters/sample/   |
+---------------------------+--------------------------+
                            |
                            v
+------------------------------------------------------+
|                Optional LLM Provider                  |
|  Disabled by default; advisory output only            |
+------------------------------------------------------+
```

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
| Packaging | Docker, Debian `.deb`, CLI entry point `alters-lab` |
| CI | GitHub Actions (backend tests + frontend build) |

## Project Layout

```
alters-lab/
  apps/
    api/                          # FastAPI backend
      src/alters_lab/
        api/                      # Route modules
        services/                 # Business logic modules
        schemas/                  # Pydantic schemas
        repositories/             # DataRepo (unified data access)
        cli/                      # CLI entry point
        main.py                   # App factory and router registration
    web/                          # React frontend
      src/
        pages/                    # Page components
        components/               # Shared UI components
        hooks/                    # TanStack Query hooks
        api.ts                    # HTTP client functions
        App.tsx                   # Root component and layout
        locales/                  # en.json, zh.json
      vite.config.ts              # Dev proxy to backend
      package.json
  alters/                         # Runtime data directory
    current/                      # Active user data (gitignored)
    product/                      # Runtime product data (mostly gitignored)
    sample/                       # Sample data for onboarding
  docs/                           # Project documentation
  .github/workflows/              # CI pipeline
```

## Backend Architecture

### Entry Point

`apps/api/src/alters_lab/main.py` creates the FastAPI application, configures middleware, registers routers, and serves the packaged frontend build when available.

### Middleware Stack

1. **CORS** -- Dev mode allows local development origins; packaged mode is restricted to local app origins.
2. **Rate Limiting** -- Custom `RateLimitMiddleware` with per-IP sliding window limits.
3. **Error Handling** -- Typed `AppError` responses plus a generic unhandled-error handler with request IDs.

### API Router Groups

| Group | Examples | Purpose |
|------|----------|---------|
| Core pipeline | `snapshot_intake`, `branches`, `alters`, `generation_drafts`, `draft_review` | Capture current state, discover branches, generate and review alters |
| Dialogue and calibration | `alter_dialogue`, `calibration_loop`, `weekly_review_session`, `calibration_conversation`, `calibration_scorecard`, `calibration_loop` prediction-accuracy | Dialogue, weekly reviews, explicit scores, prediction-accuracy checks, and calibration history |
| Forecast and evidence | `branch_forecast`, `forecast_snapshot`, `external_evidence`, `forecast_evaluation`, `predictor_profile`, `branch_outcome_targets` | Directional forecasts, locked snapshots, real-world outcomes, and evaluation |
| Optional reference context | `public_prior`, `literature_priors`, `branch_base_rate_anchor` | Compatibility endpoints for optional reference context; not a public-dataset marketing surface |
| Provider integration | `provider_gateway`, `provider_dialogue`, `provider_adapter`, `provider_config` | Disabled-by-default LLM provider configuration and advisory generation |
| Data management | `storage_boundary`, `p6_data_retention`, `user_workflow`, `product_surface`, `archive_mechanism` | Storage boundaries, retention, export, and workflow state |
| Reporting and validation | `behavior_validation`, `pattern_review`, `trend_analysis`, `dynamic_weight`, `pattern_adjustment`, `behavior_metrics` | Behavior validation, pattern detection, and trend analysis |
| Runtime | `runtime_layout`, `local_app` | Filesystem layout and frontend static serving |

### Data Repository

`apps/api/src/alters_lab/repositories/data_repo.py` implements a unified, atomic I/O layer for YAML/JSON data. Services receive a `DataRepo` through FastAPI dependency injection. It handles:

- Path resolution via `RuntimeLayout`
- Atomic writes
- Backup creation before overwrites
- SHA-256 hashing for integrity checks
- JSONL audit-log appending

### Service Layer

Services implement business logic across persistence, data safety, LLM integration, forecasting, calibration, behavior tracking, and runtime concerns. Compatibility names such as `public_prior` and `population_baseline` may remain in code or schema files, but public copy should describe that layer as optional external reference context.

Important service areas:

- **Forecast**: `branch_forecast`, `forecast_snapshot`, `forecast_evaluation`, `personal_prior_adapter`, `public_prior`, `literature_priors`, `external_evidence`, `branch_base_rate_anchor`
- **Calibration**: `calibration_loop`, `calibration_conversation`, `calibration_divergence`, `calibration_scorecard`, `rubric_delta`, `alter_rubric_baseline`
- **Behavior tracking**: `behavior_metrics`, `behavior_metric_trend`, `behavior_validation`, `pattern_review`, `pattern_adjustment`
- **Runtime**: `runtime_layout`, `p6_runtime`, `local_app`, `local_launcher`

### Schema Layer

Pydantic schemas define request and response models. Important schema groups include calibration conversation drafts, forecast snapshots, external evidence, forecast evaluation, calibration scorecards, alter rubric baselines, and optional reference artifacts. Guardrails enforce no `life_score`, no unsupported exact personal probability, and explicit user submission for reality scores.

## Frontend Architecture

### Root Component and Layout

`App.tsx` wraps the application in:

- `ErrorBoundary` for rendering errors
- `BrowserRouter` for routing
- `ToastProvider` for notifications
- `NavigationProvider` for sidebar and mobile navigation state

The desktop layout uses a fixed sidebar and scrollable content area. The mobile layout uses full-width content with a bottom tab bar.

### Main Routes

| Route | Purpose |
|------|---------|
| `/dashboard` | Main overview |
| `/status` | System health and runtime status |
| `/getting-started` | Onboarding flow |
| `/weekly` | Weekly review wizard |
| `/dialogue` | Alter dialogue |
| `/reality` | Explicit action/reality score submission |
| `/history` | Calibration history |
| `/rubric` | Pending standard/rubric suggestions |
| `/checkpoint` | Milestone/checkpoint planning |
| `/provider` | LLM provider settings |
| `/patterns` | Pattern review |
| `/validation` | Progress validation |
| `/data` | Data export and deletion |
| `/predictor-profile` | Personal profile and traits |
| `/outcome-targets` | Outcome goals and thresholds |
| `/branch-forecast` | Directional branch forecast |
| `/forecast-calibration` | Forecast snapshots, evidence, evaluations, and scorecard |
| `/public-priors` | Optional reference-context compatibility page |
| `/calibration-conversation` | LLM-assisted calibration drafts |
| `/behavior-metrics` | Behavior metric trends |

### Data Layer

All frontend API communication goes through `src/api.ts` and domain-specific hooks in `src/hooks/`. Hooks use TanStack Query for reads, mutations, and cache invalidation. Vite dev server proxies API paths to `http://localhost:18790`.

## Data Flow

### Calibration Conversation Flow

```
User
  --> CalibrationConversation page
    --> POST /calibration-conversation/...
      --> calibration_conversation service
        --> optional provider_adapter call
        --> draft structured calibration data
  --> User reviews extracted data
    --> confirm/reject draft
      --> calibration services update records only after explicit user confirmation
```

Provider output is advisory. It cannot auto-submit reality scores or silently modify active user data.

### Prediction Accuracy Flow

```
Alter YAML (personality_drift directions)
  --> alter_rubric_baseline service
    --> Maps ↑↓→ directions to rubric dimension expected scores
    --> Produces AlterRubricBaseline (initial/30d/90d predictions)

User calibration scores (from calibration conversation)
  --> confirm_draft writes RealityScoreRecord with branch_id
    --> Uses alter baseline as expected_scores (instead of self-vs-self)

GET /calibration-loop/prediction-accuracy?branch_id=branch_D
  --> Compares alter baseline predictions vs actual trajectory
  --> Returns per-dimension alignment + overall assessment:
      on_track / partial_match / diverging / failure_mode_emerging
```

### Simulation / Forecast Flow

```
User sets predictor profile & outcome targets
  --> User requests forecast
    --> Personal evidence is evaluated first
    --> Optional reference context is considered only if available and appropriate
    --> Adapter surfaces agreement, conflict, confidence, and readiness
    --> forecast_snapshot locks the result before outcomes are known

User records real-world evidence
  --> forecast_evaluation compares prediction vs outcome
    --> calibration_scorecard aggregates hit/miss/partial/unknown results
```

## Key Design Decisions

1. **Local-first storage** -- All data is stored as YAML/JSON files on disk for simple backups and user inspection.
2. **Human confirmation gates** -- Provider output and calibration drafts require explicit user review before becoming data.
3. **No single life score** -- The system never reduces life quality to a single `life_score`.
4. **No unsupported exact probabilities** -- Directional outputs are the default. Exact probability requires a separately validated and approved artifact.
5. **Optional reference context only** -- External sources are background context, not individual predictions or marketing proof.
6. **Locked forecasts before evaluation** -- Forecast snapshots are recorded before outcomes to preserve auditability.
7. **Separate evidence sources** -- Personal evidence, reference context, adapter output, and external outcomes remain distinguishable.
8. **Packaging mode separation** -- Runtime layout resolves paths differently for development mode versus packaged mode.

## Data Storage

All data lives under the `alters/` directory as YAML and JSON files. No database is required.

```
alters/
  current/                # Active user data
  sample/                 # Sample data
  product/                # Runtime product data
    weekly_notes/
    weekly_reviews/
    calibration_records/
    behavior_metrics/
    predictor_profiles/
    branch_outcome_targets/
    forecast_snapshots/
    external_evidence/
    forecast_evaluations/
    calibration_drafts/
    calibration_conversations/
    exports/
  calibration/            # Rubric and calibration state
  archive/                # Completed cycles / checkpoints
```

Key data entities are defined in `docs/data-model.md`.

## Packaging and Deployment

### Docker

The root `Dockerfile` builds the Vite frontend, installs the FastAPI backend, copies the frontend build into the packaged app, and starts uvicorn on port `18790`.

### Debian Package

The app can also be built as a `.deb` package. `runtime_layout` resolves paths differently for development mode versus packaged mode.

## CI/CD

GitHub Actions runs backend tests and frontend build checks on pushes and pull requests. The app has no automatic deployment step; it runs locally unless deployed separately.

## Sample Data

The `alters/sample/` directory contains pre-built sample data for new users. `alters-lab load-sample` copies this into `alters/current/`. It skips files that already exist unless `--force` is passed.
