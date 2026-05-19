# Alters Lab API

FastAPI backend for the Alters Lab personal future-branch simulation system.

## Overview

Provides in-memory Snapshot Intake workflow and YAML export service. No database, no frontend, no LLM provider integration.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| GET | `/snapshot-intake/health` | Snapshot intake component health |
| POST | `/snapshot-intake/sessions` | Create new intake session |
| GET | `/snapshot-intake/sessions/{id}` | Get session by ID |
| GET | `/snapshot-intake/sessions/{id}/next-anchor` | Get next pending anchor |
| POST | `/snapshot-intake/sessions/{id}/answers` | Submit anchor answer |
| POST | `/snapshot-intake/sessions/{id}/confirm` | Confirm completed snapshot |
| GET | `/cycle-summary/health` | Cycle summary component health |
| GET | `/cycle-summary/current` | Sealed active YAML chain summary |
| GET | `/cycle-summary/validation` | Validation result and artifact count |
| GET | `/cycle-summary/artifacts` | Artifact metadata (no YAML content) |
| GET | `/evidence/health` | Evidence reports component health |
| GET | `/evidence/status` | Evidence status summary |
| GET | `/evidence/reports` | Evidence report list |
| GET | `/evidence/active-yaml-validation` | Active YAML validation result |
| GET | `/evidence/day30-demo` | Day 30 demo evidence |
| GET | `/evidence/phase1-closeout` | Phase 1 closeout evidence |
| GET | `/branches/health` | Branches controlled write health |
| POST | `/branches/persist` | Persist reviewed branches payload through controlled write API |
| GET | `/alters/health` | Alters controlled write health |
| POST | `/alters/persist/{alter_id}` | Persist single alter through controlled write API |
| POST | `/alters/persist-batch` | Persist all 4 alters through controlled write API |
| GET | `/generation-drafts/health` | Generation drafts component health |
| POST | `/generation-drafts/preview` | Preview generation draft (draft-only, no active write) |
| GET | `/generation-drafts/list` | List generation drafts |
| GET | `/draft-review/health` | Draft review boundary health |
| POST | `/draft-review/{draft_id}/review` | Review draft and prepare promotion package |
| GET | `/draft-review/list` | List draft reviews |
| GET | `/promotion-orchestration/health` | Promotion orchestration plan-only health |
| POST | `/promotion-orchestration/{draft_id}/plan` | Create orchestration plan from promotion package |
| GET | `/promotion-orchestration/list` | List orchestration plans |
| GET | `/promotion-execution-gate/health` | Promotion execution gate health |
| POST | `/promotion-execution-gate/{draft_id}/check` | Run execution gate check (dry-run, prerequisites, execution packet) |
| GET | `/promotion-execution-gate/list` | List execution gate reports |
| GET | `/promotion-live-execution/health` | Promotion live execution health |
| POST | `/promotion-live-execution/{draft_id}/run` | Run live execution (dry-run or live with path_overrides) |
| GET | `/promotion-live-execution/list` | List live execution reports |

## Services

- **snapshot_intake** — Pure state-transition functions for the intake workflow
- **snapshot_sessions** — In-memory session store
- **snapshot_export** — Serialize completed snapshots to canonical YAML
- **cycle_summary** — Read-only endpoints over the sealed active YAML chain (Phase 2)
- **evidence_reports** — Read-only evidence status, reports, and Day 30 demo
- **controlled_write** — Shared helpers for controlled YAML persistence
- **branches_persist** — Branches controlled write service
- **alters_persist** — Alters controlled write service
- **generation_drafts** — Deterministic draft-only generation runtime
- **draft_review** — Draft review and promotion boundary
- **promotion_orchestration** — Promotion orchestration plan-only boundary
- **promotion_execution_gate** — Promotion execution gate (dry-run, prerequisites, execution packet)
- **promotion_live_execution** — Controlled live execution runtime (dry-run/live, path_overrides, controlled persist)

## Export

Export functions (`snapshot_to_canonical_dict`, `snapshot_to_yaml`, `write_snapshot_yaml`) require a completed snapshot. The API confirm endpoint remains in-memory only — it does not write files.

## Run

```bash
pip install -e ".[dev]"
uvicorn alters_lab.main:app --reload
pytest
```
