# P5 Local Release Candidate

## Overview

P5 turns the backend calibration loop into a locally usable product MVP.

- Single-user, local-only
- No cloud deployment
- No production auth
- No database
- YAML remains default storage

## Backend Start

```bash
cd apps/api
uvicorn alters_lab.main:app --reload --port 8000
```

Default provider mode: **mock**. No real LLM calls are made unless explicitly configured via environment variables.

## Frontend Start

```bash
cd apps/web
npm install
npm run dev
```

The frontend proxies API requests to `localhost:8000` via Vite dev server config.

## Default Provider Explanation

- `ALTERS_PROVIDER_MODE=mock` (default): returns deterministic simulated replies
- `ALTERS_PROVIDER_MODE=disabled`: rejects all provider calls
- `ALTERS_PROVIDER_MODE=openai_compatible_http`: uses HTTP to any OpenAI-compatible endpoint (requires `ALTERS_PROVIDER_BASE_URL` and `ALTERS_PROVIDER_API_KEY`)

Real provider mode is **disabled by default**. No API keys are stored or committed.

## Optional Real Provider Env Template

```bash
# .env.local (DO NOT COMMIT)
ALTERS_PROVIDER_MODE=openai_compatible_http
ALTERS_PROVIDER_BASE_URL=https://your-provider.example.com/v1
ALTERS_PROVIDER_API_KEY=your-key-here
ALTERS_PROVIDER_MODEL=your-model-name
```

## Local Workflow Demo

1. **Start API:** `cd apps/api && uvicorn alters_lab.main:app --reload --port 8000`
2. **Start Frontend:** `cd apps/web && npm install && npm run dev`
3. **Select Alter:** Navigate to Dialogue page, select alter_A/B/C/D
4. **Send Dialogue Message:** Type a message, click Send — receive mock/provider-backed reply
5. **Submit Reality Score:** Navigate to Reality Score page, adjust sliders, submit
6. **View History/Drift:** Navigate to History page — see scores and drift evidence
7. **Generate Rubric Suggestion:** Navigate to Rubric Delta page — generate suggestion (pending_review)
8. **Generate Checkpoint Plan:** Navigate to Checkpoint Plan page — generate plan (pending_review)

## Safety Notes

- **No active YAML auto-write:** `alters/current/**` is read-only from all P5 surfaces
- **Provider output not auto-persisted:** `save_session` defaults to `false`
- **Rubric suggestions pending_review only:** Generated suggestions are not applied automatically
- **Checkpoint plan pending_review only:** Generated plans are not executed automatically
- **No secrets committed:** API keys are never returned by API or written to disk
- **Frontend calls only safe endpoints:** No calls to promotion-live-execution, controlled persist, or archive create
- **YAML remains default:** No database migration implemented

## API Routes Added

| Route | Method | Purpose |
|---|---|---|
| `/product/health` | GET | Product health check |
| `/product/routes` | GET | Route inventory with classification |
| `/product/status` | GET | System status summary |
| `/product/workflow-capabilities` | GET | Available workflow capabilities |
| `/provider-gateway/health` | GET | Provider gateway health |
| `/provider-gateway/complete` | POST | Provider completion request |
| `/provider-gateway/config-status` | GET | Provider config (redacted) |
| `/provider-dialogue/health` | GET | Dialogue service health |
| `/provider-dialogue/{alter_id}/reply` | POST | Alter dialogue reply |
| `/storage-boundary/health` | GET | Storage boundary health |
| `/storage-boundary/manifest` | GET | Storage path classification |
| `/user-workflow/health` | GET | Workflow health |
| `/user-workflow/state` | GET | Integrated workflow state |
| `/user-workflow/run-summary` | POST | Save workflow run record |
| `/phase5-closeout/health` | GET | Closeout health |
| `/phase5-closeout/report` | GET | Safety closeout report |
| `/phase5-closeout/evidence` | GET | Closeout evidence |
