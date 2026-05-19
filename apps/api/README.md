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

## Services

- **snapshot_intake** — Pure state-transition functions for the intake workflow
- **snapshot_sessions** — In-memory session store
- **snapshot_export** — Serialize completed snapshots to canonical YAML
- **cycle_summary** — Read-only endpoints over the sealed active YAML chain (Phase 2)

## Export

Export functions (`snapshot_to_canonical_dict`, `snapshot_to_yaml`, `write_snapshot_yaml`) require a completed snapshot. The API confirm endpoint remains in-memory only — it does not write files.

## Run

```bash
pip install -e ".[dev]"
uvicorn alters_lab.main:app --reload
pytest
```
