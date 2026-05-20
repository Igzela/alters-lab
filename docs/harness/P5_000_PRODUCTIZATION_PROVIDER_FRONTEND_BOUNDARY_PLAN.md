# P5-000: Productization / Provider / Frontend Boundary Plan

## Identity

P5 is the **Local Product MVP** phase. It turns the backend calibration loop into a locally usable product without cloud deployment, multi-user support, or production infrastructure.

## Product Goal

- Usable local loop: select alter → dialogue → score → calibrate → review
- No hosted SaaS, no production auth, no billing
- Single-user, local-only, file-based storage remains default

## Default Provider Mode

- **mock**: always available, returns deterministic simulated replies
- **disabled**: rejects all provider calls
- **openai_compatible_http**: optional, env-gated, HTTP-only (no SDK dependency)

Default is `mock`. Real provider mode is disabled unless explicitly configured via environment variables.

## Frontend Scope

- Minimal UI: Vite + React + TypeScript
- No auth, no database, no heavy design system
- Calls only safe product API endpoints
- No direct file access, no provider key exposure

## Storage Scope

- YAML remains the default storage backend
- No database migration (SQLite/Postgres deferred)
- Storage adapter describes boundaries:
  - Active YAML: read-only
  - Calibration scores: write area
  - Product sessions: write area (ignored by default)
  - Evidence: committed area

## Active YAML Safety

- **No frontend or provider writes to active YAML**
- `alters/current/**` is read-only from all P5 surfaces
- `alters/calibration/rubric.yaml` is read-only
- Provider output is never auto-promoted to active YAML

## Dialogue Safety

- Provider replies are **not facts** and **not persistent by default**
- `save_session=true` writes only to `alters/product/sessions/` (ignored by default)
- Saved sessions must not contain API keys
- Saved sessions must include: provider mode, model, timestamp, alter_id, user_message, reply_text, safety metadata

## Persistent Writes (Explicit Only)

| Write Type | Destination | Trigger |
|---|---|---|
| Reality scores | `alters/calibration/scores/` | Explicit user submission |
| Dialogue sessions | `alters/product/sessions/` | Explicit `save_session=true` |
| Workflow runs | `alters/product/workflow_runs/` | Explicit save |
| Rubric suggestions | `alters/calibration/rubric_delta_suggestions/` | Explicit suggestion generation (pending_review) |
| Checkpoint plans | `alters/calibration/checkpoint_plans/` | Explicit plan generation (pending_review) |

## Forbidden

- Provider output auto-promoted to active YAML
- Frontend calling promotion-live-execution
- Automatic rubric write
- Automatic regeneration of branches/alters/snapshots
- Automatic archive creation
- Secret commit (API keys, .env)
- Multi-user authentication
- Database migration
- P6 scope execution

## P5 Exit Gate

All must pass:

1. Local app starts (`uvicorn` serves API)
2. User selects an alter (from A/B/C/D)
3. User gets provider/mock-backed reply
4. User submits reality score (explicit)
5. User sees drift/calibration history
6. User sees rubric delta suggestion (pending_review)
7. User sees checkpoint plan (pending_review)
8. Safety closeout passes (no active YAML diff, no secrets, no dangerous frontend calls)

## Module Inventory

| Module | Schemas | Services | API | Tests |
|---|---|---|---|---|
| P5-M1 Product Surface | product_surface.py | product_surface.py | product_surface.py | test_product_surface*.py |
| P5-M2 Provider Gateway | provider_gateway.py | provider_gateway.py | provider_gateway.py | test_provider_gateway*.py |
| P5-M3 Provider Dialogue | provider_dialogue.py | provider_dialogue.py | provider_dialogue.py | test_provider_dialogue*.py |
| P5-M4 Frontend | N/A | N/A | N/A | build + grep checks |
| P5-M5 Storage Boundary | storage_boundary.py | storage_boundary.py | storage_boundary.py | test_storage_boundary*.py |
| P5-M6 User Workflow | user_workflow.py | user_workflow.py | user_workflow.py | test_user_workflow*.py |
| P5-M7 Closeout | phase5_closeout.py | phase5_closeout.py | phase5_closeout.py | test_phase5_closeout*.py |
| P5-M8 Release RC | N/A | N/A | N/A | docs only |
