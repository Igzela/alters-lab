# Architecture

## System Overview

Alters Lab is a personal future-path simulation and calibration system. It helps users explore structurally different life branches, engage in dialogue with hypothetical "alter" versions of themselves, score branches against their values, and calibrate predictions over time. All data is stored as YAML/JSON files on disk -- no database.

```
+------------------------------------------------------+
|                   Frontend (React)                    |
|  Pages (21 routes) + Hooks (20 modules) + Components |
+---------------------------+--------------------------+
                            | HTTP (fetch)
                            v
+------------------------------------------------------+
|                   Backend (FastAPI)                    |
|  API Layer (58 modules) --> Services (69 modules)    |
|  DataRepo (atomic YAML/JSON I/O)                     |
+---------------------------+--------------------------+
                            |
                            v
+------------------------------------------------------+
|              Data Storage (YAML/JSON files)            |
|  alters/current/ + alters/sample/                    |
+------------------------------------------------------+
                            |
                            v
+------------------------------------------------------+
|                External LLM Provider                   |
|  (OpenAI, Anthropic, etc. via provider_adapter)      |
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
| Packaging | Debian `.deb`, CLI entry point `alters-lab` |
| CI | GitHub Actions (backend tests + frontend build) |

## Project Layout

```
alters-lab/
  apps/
    api/                          # FastAPI backend
      src/alters_lab/
        api/                      # 58 route modules
        services/                 # 69 service modules
        schemas/                  # 64 Pydantic schema modules
        repositories/             # DataRepo (unified data access)
        cli/                      # CLI entry point (launcher.py)
        main.py                   # App factory, middleware, router registration
        errors.py                 # AppError exception hierarchy
        middleware.py             # Rate limiting
        logging_config.py         # Structured logging
      tests/                      # pytest + httpx tests (1970 tests)
      pyproject.toml              # Python package config
    web/                          # React frontend (84 tests)
      src/
        pages/                    # 21 page components (21 active routes)
        components/               # 22 shared UI components
        hooks/                    # 20 hook modules (75+ exported hooks)
        api.ts                    # HTTP client functions
        types.ts                  # TypeScript type definitions
        App.tsx                   # Root component, layout
        i18n.ts                   # i18next config (en, zh)
        locales/                  # en.json, zh.json
      vite.config.ts              # Dev proxy to backend
      package.json
  alters/                         # Runtime data directory
    current/                      # Active user data
    sample/                       # Sample data for onboarding
  docs/                           # Project documentation
  .github/workflows/              # CI pipeline
```

## Backend Architecture

### Entry Point

`apps/api/src/alters_lab/main.py` creates the FastAPI application. The lifespan context manager calls `setup_logging()` on startup and logs shutdown. The app title is "Alters Lab API" and version is 0.1.0.

### Middleware Stack

1. **CORS** -- `CORSMiddleware`. Dev mode allows `["*"]`; packaged mode restricts to `localhost:18790`.
2. **Rate Limiting** -- Custom `RateLimitMiddleware` (per-IP sliding window, 600 requests per 60 seconds). Returns 429 with JSON error body when exceeded.

### Error Handling

Two global exception handlers:
- `AppError` -- typed application errors with status code, error code, and message. Generates a request ID per request.
- `Exception` -- unhandled errors return 500 with a generic message and request ID. Logged with full traceback.

### Health Endpoint

`GET /health` returns `{"status": "ok", "service": "alters-lab-api"}`. Used by CLI doctor checks and CI.

### API Routers (58 modules)

All routers live in `apps/api/src/alters_lab/api/`. Each module defines a FastAPI `APIRouter`. Routers are registered in `main.py` via `app.include_router()` from a `_ROUTER_MODULES` list.

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
| `calibration_conversation` | `/calibration-conversation` | LLM-driven calibration data extraction via chat |
| `calibration_divergence` | `/calibration-divergence` | Track divergence between predicted and actual calibration |
| `calibration_scorecard` | `/calibration-scorecard` | Aggregate calibration accuracy tracking |
| `calibration_loop` (prediction-accuracy) | `/calibration-loop/prediction-accuracy` | Compare alter baseline predictions against actual calibration trajectory |

#### Forecast Pipeline

| Router | Prefix | Purpose |
|--------|--------|---------|
| `branch_forecast` | `/branch-forecast` | Route A + Route B + Adapter combined forecasts |
| `branch_base_rate_anchor` | `/branch-base-rate-anchor` | Base rate anchoring for branch forecasts |
| `forecast_snapshot` | `/forecast-snapshot` | Locked immutable forecast records |
| `external_evidence` | `/external-evidence` | Real-world observation recording |
| `forecast_evaluation` | `/forecast-evaluation` | Prediction vs outcome comparison |
| `branch_outcome_targets` | `/branch-outcome-targets` | Measurable outcome goals per branch/domain |
| `predictor_profile` | `/predictor-profile` | Trait baselines and current context |

#### Population Baseline

| Router | Prefix | Purpose |
|--------|--------|---------|
| `public_prior` | `/public-prior` | Population prior integration and management |
| `literature_priors` | `/literature-priors` | Literature-based prior extraction |

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
| `behavior_metrics` | `/behavior-metrics` | Weekly behavioral indicators, catalog, milestone validation |
| `behavior_metric_trend` | `/behavior-metric-trend` | Within-person behavior metric trend analysis (Route A) |

#### Runtime and Infrastructure

| Router | Prefix | Purpose |
|--------|--------|---------|
| `runtime_layout` | `/runtime-layout` | Resolve filesystem layout (dev vs packaged) |
| `local_app` | `/local-app` | Serve frontend static files and manage local app |

### Data Repository

`apps/api/src/alters_lab/repositories/data_repo.py` implements a `DataRepo` class that provides unified, atomic I/O for all YAML/JSON data operations. Services receive a `DataRepo` instance via FastAPI `Depends()`. This replaces 35+ scattered `yaml.safe_load`/`safe_dump` call sites with a single interface that handles:

- Path resolution via `RuntimeLayout` (dev vs packaged mode)
- Atomic writes (write to temp file, then rename)
- Backup creation before overwrites
- SHA-256 hashing for integrity checks
- JSONL audit log appending

### Service Layer

69 service modules in `apps/api/src/alters_lab/services/` implement business logic. Services are imported by API routers and handle:

- **Persistence**: `alters_persist`, `branches_persist`, `snapshot_persist`, `snapshot_sessions`, `snapshot_export`, `controlled_write`
- **Data safety**: `data_safety` (backup planning, archive creation)
- **LLM integration**: `provider_adapter`, `provider_gateway`, `provider_dialogue`, `provider_config`, `provider_connectivity`
- **Runtime**: `runtime_layout`, `p6_runtime`, `local_app`, `local_launcher`
- **Forecast**: `branch_forecast`, `forecast_snapshot`, `forecast_evaluation`, `personal_prior_adapter`, `public_prior`, `literature_priors`, `external_evidence`, `branch_base_rate_anchor`
- **Calibration**: `calibration_loop`, `calibration_conversation`, `calibration_divergence`, `calibration_scorecard`, `rubric_delta`, `alter_rubric_baseline`
- **Behavior tracking**: `behavior_metrics`, `behavior_metric_trend`, `behavior_validation`, `pattern_review`, `pattern_adjustment`
- **Core logic**: One service per domain area, mirroring the router structure

### Schema Layer

64 Pydantic schema modules in `apps/api/src/alters_lab/schemas/` define request/response models. Each schema module typically corresponds to one API router. Notable schemas include `calibration_conversation` (LLM-driven calibration chat), `personal_prior_adapter` (strength-aware forecast blending), and `population_baseline` (public prior management).

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

### Root Component and Layout

`App.tsx` wraps the application in:
- `ErrorBoundary` -- catches React rendering errors
- `BrowserRouter` -- React Router for hash-based routing
- `ToastProvider` -- toast notification system
- `NavigationProvider` -- custom navigation context (replaces direct React Router for sidebar/mobile coordination)

Layout:
- **Desktop** (>= 768px): Fixed 220px sidebar + scrollable content area (max-width 1080px)
- **Mobile** (< 768px): Full-width content + bottom tab bar navigation
- Skip-to-content accessibility link
- Dark/light theme toggle (via `ThemeContext`)

### Routing

React Router (`BrowserRouter`) with lazy-loaded page components via `PageRouter.tsx`. 21 active routes:

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | Dashboard | Main dashboard overview |
| `/dashboard` | Dashboard | Main dashboard overview |
| `/status` | SystemStatus | System health and overview |
| `/weekly` | WeeklyReview | Weekly review session (multi-step wizard) |
| `/dialogue` | AlterDialogue | Alter conversation interface |
| `/reality` | RealityScore | Reality scoring and divergence tracking |
| `/history` | CalibrationHistory | Historical calibration data |
| `/rubric` | RubricDelta | Rubric evolution over time |
| `/checkpoint` | CheckpointPlan | Checkpoint planning and regeneration |
| `/provider` | ProviderSettings | LLM provider configuration |
| `/getting-started` | GettingStarted | Onboarding flow |
| `/patterns` | PatternReview | Pattern analysis across cycles |
| `/validation` | BehaviorValidation | System behavior validation |
| `/data` | DataManagement | Data management and retention |
| `/predictor-profile` | PredictorProfile | Trait baselines and context |
| `/outcome-targets` | OutcomeTargets | Measurable outcome goals |
| `/branch-forecast` | BranchForecast | Combined forecast view |
| `/forecast-calibration` | ForecastCalibration | Forecast calibration tracking |
| `/public-priors` | PublicPriors | Population baseline priors |
| `/calibration-conversation` | CalibrationConversation | LLM-driven calibration chat |
| `/behavior-metrics` | BehaviorMetricsDetail | Behavioral metrics detail view |

`P6Progress.tsx` exists in `pages/` but is not currently routed.

### Weekly Review Wizard

The `WeeklyReview` page (`pages/weekly-review/`) implements a multi-step wizard:
- `WeeklyWizard.tsx` -- wizard container with step management via `wizardReducer.ts`
- `StepAssistant.tsx` -- AI-assisted review step
- `StepComplete.tsx` -- completion step
- `StepNoteEdit.tsx` -- note editing step
- `StepNoteIngest.tsx` -- Obsidian note ingestion step
- `StepReview.tsx` -- review step
- `StepScoring.tsx` -- scoring step
- `types.ts` -- wizard type definitions

### Data Layer

All API communication goes through `src/api.ts` (HTTP client functions) and `src/hooks/` (20 hook modules with 75+ exported TanStack Query hooks). The hooks use `useQuery` for reads and `useMutation` for writes, with automatic cache invalidation on mutations.

Vite dev server proxies API paths to `http://localhost:18790` (see `vite.config.ts`).

Hook modules are split by domain:

| Module | Domain | Key hooks |
|--------|--------|-----------|
| `useApi.ts` | Re-export barrel | Re-exports from all domain modules |
| `useWeeklyNoteHooks.ts` | Weekly notes | `useWeeklyNotes`, `useIngestWeeklyNote`, `useEditWeeklyNote` |
| `useWeeklyReviewHooks.ts` | Weekly review | `useWeeklyReviews`, `useStartWeeklyReview`, `useCompleteWeeklyReview`, `useWeeklyReviewAssistantStatus`, `useSuggestWeeklyReviewAssistant` |
| `useActionAlignmentHooks.ts` | Action alignment | `useActionAlignmentScores`, `useScoreActionAlignment` |
| `useProviderHooks.ts` | LLM providers | `useProviderConfig`, `useUpdateProviderConfig`, `useProviderStatus`, `useStoreSecret`, `useDeleteSecret`, `useTestProvider` |
| `useAnalysisHooks.ts` | Analysis | `useTrendAnalysis`, `useDynamicWeights`, `usePatternAdjustment` |
| `useForecastHooks.ts` | Forecasting | 8 hooks for forecast pipeline |
| `usePredictionHooks.ts` | Predictions | 8 hooks for prediction pipeline |
| `useCalibrationConversationHooks.ts` | Calibration chat | 6 hooks for LLM-driven calibration |
| `usePublicPriorHooks.ts` | Population priors | 5 hooks for public prior management |
| `usePatternReviewHooks.ts` | Pattern review | 3 hooks for pattern analysis |
| `useBehaviorMetricsHooks.ts` | Behavior metrics | `useBehaviorMetrics` |
| `useBehaviorValidationHooks.ts` | Validation | 2 hooks for behavior validation |
| `useCalibrationHooks.ts` | Calibration | 2 hooks for calibration data |
| `useAlterHooks.ts` | Alters | 2 hooks for alter CRUD |
| `useSystemHooks.ts` | System | 3 hooks for system status |
| `useDataHooks.ts` | Data management | 3 hooks for data operations |
| `useMiscHooks.ts` | Miscellaneous | 3 hooks for uncategorized endpoints |
| `useQueryKeys.ts` | Cache keys | Centralized query key factory |

### Component Library

22 shared components in `src/components/`:

| Component | Purpose |
|-----------|---------|
| `Badge` | Status/count badges |
| `Banner` | Alert/info banners |
| `Button` | Styled button with variants |
| `Card` | Content container |
| `ErrorBoundary` | React error boundary |
| `ErrorDisplay` | API error rendering |
| `Input` | Styled text input |
| `KeyboardShortcuts` | Global keyboard shortcut handler |
| `LoadingSpinner` | Loading indicator |
| `MobileNav` | Bottom tab bar (mobile) |
| `NavigationContext` | Navigation state provider |
| `PageRouter` | Route definitions with lazy loading |
| `ProgressBar` | Progress indicator |
| `ShortcutHelp` | Keyboard shortcut help overlay |
| `Sidebar` | Desktop navigation sidebar |
| `Skeleton` | Loading skeleton |
| `ThemeContext` | Dark/light theme provider |
| `Toast` | Toast notification system (ToastProvider + useToast) |

### Internationalization

i18next with two locales (`en.json`, `zh.json`). Language persisted to `localStorage` under key `alters_lab_language`. Default language is English. Components use the `useTranslation` hook and `t()` function for all user-facing strings.

## Data Flow

### Calibration Conversation Flow

```
User (frontend)
  --> CalibrationConversation page
    --> useCalibrationConversationHooks (TanStack Query)
      --> POST /calibration-conversation/chat
        --> calibration_conversation router
          --> calibration_conversation service
            --> provider_adapter (LLM call)
            --> Returns structured calibration data
  --> User reviews extracted data
    --> POST /calibration-conversation/confirm
      --> calibration_loop service (updates calibration state)
```

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
  --> PredictorProfile page + OutcomeTargets page
    --> predictor_profile service + branch_outcome_targets service

User requests forecast
  --> BranchForecast page
    --> useForecastHooks
      --> POST /branch-forecast/calculate
        --> branch_forecast service
          --> Route A: behavior_metric_trend (within-person trends)
          --> Route B: public_prior (population baseline) + personal_prior_adapter (strength-aware blending)
          --> Combined forecast with confidence intervals
          --> forecast_snapshot service (locks result)

User records external evidence
  --> POST /external-evidence/record
    --> external_evidence service (stores observation)

User evaluates forecast
  --> forecast_evaluation service (prediction vs outcome comparison)
    --> calibration_scorecard (aggregate accuracy tracking)
```

### Prior Update Flow

```
Population prior pipeline:
  literature_priors --> public_prior --> personal_prior_adapter
    --> Strength-aware blending with Route A predictions
    --> public_prior router manages CRUD for population baselines
    --> personal_prior_adapter adjusts blend weight based on forecast strength

Individual prior pipeline:
  calibration_loop --> calibration_conversation (LLM extraction)
    --> calibration_divergence (predicted vs actual tracking)
    --> behavior_metric_trend (Route A within-person trends)
    --> pattern_adjustment (behavioral pattern corrections)
```

## Key Design Decisions

1. **No database** -- All data stored as YAML/JSON files on disk. Enables simple backups, human-readable inspection, and no external dependencies. The `DataRepo` class provides atomic writes and integrity checking.

2. **Dependency injection via FastAPI** -- Services receive `DataRepo` via `Depends()`, enabling testability and decoupling from filesystem.

3. **Dual forecast routes** -- Route A (within-person behavioral trends) and Route B (population baseline with personal prior adapter) are combined with strength-aware blending. Strong forecasts use more Route B; weak forecasts lean on Route A.

4. **LLM-driven calibration** -- Rather than manual data entry, the calibration conversation endpoint uses an LLM to extract structured calibration data from natural language dialogue.

5. **Phase closeout pattern** -- Each major phase (3-6) has a dedicated closeout router/service that validates completion and transitions system state.

6. **Lazy-loaded pages** -- All 21 page components are lazy-loaded via React `lazy()` with Suspense fallbacks, reducing initial bundle size.

7. **Domain-split hooks** -- Instead of a monolithic hook file, hooks are split into 20 domain-specific modules with a barrel re-export in `useApi.ts`.

8. **Custom navigation context** -- `NavigationContext` coordinates sidebar and mobile nav state independently from React Router, enabling consistent active-state highlighting.

9. **Packaged mode** -- The `runtime_layout` service resolves paths differently for dev mode (local source tree) vs packaged mode (system-wide install). The CLI `--mode` flag overrides auto-detection.

10. **Promotion pipeline with gate checks** -- Branch promotion goes through orchestration --> gate checks --> live execution, preventing premature action on weakly-calibrated branches.

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
- **ForecastSnapshot**: Locked immutable forecast record with confidence intervals
- **PublicPrior**: Population baseline probability for a branch/domain
- **CalibrationConversation**: LLM-driven calibration dialogue session

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
