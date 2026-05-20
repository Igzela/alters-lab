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
| GET | `/phase3-closeout/health` | Phase 3 closeout health |
| GET | `/phase3-closeout/report` | Phase 3 closeout report (read-only) |
| GET | `/phase3-closeout/evidence` | Phase 3 closeout evidence (read-only) |
| GET | `/alter-dialogue/health` | Alter dialogue runtime health |
| GET | `/alter-dialogue/alters` | List active alter metadata (no full YAML) |
| GET | `/alter-dialogue/{alter_id}/context` | Get dialogue context for an alter |
| POST | `/alter-dialogue/{alter_id}/prompt` | Build prompt packet from alter + user message |
| GET | `/calibration-loop/health` | Calibration loop component health |
| POST | `/calibration-loop/reality-scores` | Persist explicit user-submitted reality score record |
| POST | `/calibration-loop/drift/calculate` | Compute drift evidence from expected and actual scores |
| GET | `/calibration-loop/history` | Read-only calibration history and derived drift evidence |
| GET | `/rubric-delta/health` | Rubric delta suggestion health |
| POST | `/rubric-delta/suggest` | Suggest pending-review rubric deltas from repeated score mismatch |
| GET | `/rubric-delta/list` | List saved rubric delta suggestion metadata |
| GET | `/archive-mechanism/health` | Archive mechanism health |
| POST | `/archive-mechanism/plan` | Preview archive manifest without writing |
| POST | `/archive-mechanism/create` | Explicitly create copy-only checkpoint archive package |
| GET | `/archive-mechanism/list` | List archive package metadata |
| GET | `/checkpoint-regeneration/health` | Checkpoint regeneration plan health |
| POST | `/checkpoint-regeneration/plan` | Create pending-review regeneration plan from high drift evidence |
| GET | `/checkpoint-regeneration/list` | List saved checkpoint plan metadata |
| GET | `/phase4-closeout/health` | Phase 4 closeout health |
| GET | `/phase4-closeout/report` | Phase 4 closeout report (read-only) |
| GET | `/phase4-closeout/evidence` | Phase 4 closeout evidence (read-only) |

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
- **phase3_closeout** — Phase 3 read-only closeout verification gate
- **alter_dialogue** — Read-only alter dialogue context builder (P4-M1/P4-M1R, full alter YAML prompt packet, no provider)
- **calibration_loop** — P4 explicit reality score records, evidence-only drift calculation, read-only calibration history
- **rubric_delta** — P4-M5 suggestion-only rubric delta detection from calibration history; never writes rubric.yaml
- **archive_mechanism** — P4-M6 explicit-only archive planner/creator; copy-only package, source files unchanged
- **checkpoint_regeneration** — P4-M7 high-drift checkpoint plan builder; plan-only, no active regeneration
- **phase4_closeout** — Phase 4 backend calibration loop closeout verifier and evidence writer

## Export

Export functions (`snapshot_to_canonical_dict`, `snapshot_to_yaml`, `write_snapshot_yaml`) require a completed snapshot. The API confirm endpoint remains in-memory only — it does not write files.

## Alter Dialogue (P4-M1)

The Alter Dialogue Runtime provides read-only dialogue context packaging. It loads an active alter YAML, validates its contract, and returns a prompt packet for downstream use.

- **No LLM provider is called** — `provider_ready` is always `false`.
- **No assistant replies are generated** — the endpoint returns context and prompt packets only.
- **No active YAML is written** — dialogue is read-only and non-persistent.
- **No dialogue logs are persisted** — session state is not saved to files.
- **Full alter YAML is injected** — prompt packets include `full_alter_yaml`; summary-only injection is invalid.

## Calibration Loop MVP (P4-M2/M3/M4)

The Calibration Loop MVP exposes backend-only calibration contracts.

- **Reality scores are explicit user submissions** — `POST /calibration-loop/reality-scores` writes `score_*.yaml` records under `alters/calibration/scores`.
- **Drift is evidence only** — `POST /calibration-loop/drift/calculate` computes normalized drift from supplied expected and actual scores, but does not write files or trigger regeneration.
- **History is read-only** — `GET /calibration-loop/history` lists score records and derives drift evidence in memory when expected scores exist.
- **Rubric is never modified** — no endpoint writes `alters/calibration/rubric.yaml`.
- **No active YAML, frontend, database, provider, archive, promotion, or regeneration path is added.**

## Rubric Delta Suggestion (P4-M5)

Rubric delta suggestion detects repeated mismatch patterns between expected and actual reality scores.

- Suggestions stay `pending_review`.
- `rubric_write_allowed` is always `false`.
- Saving a suggestion writes only to `alters/calibration/rubric_delta_suggestions/`.
- `alters/calibration/rubric.yaml` is never modified.

## Archive Mechanism (P4-M6)

Archive mechanism is explicit-action only.

- `/archive-mechanism/plan` returns a manifest preview and writes nothing.
- `/archive-mechanism/create` copies approved active/calibration files into `alters/archive/checkpoints/archive_*`.
- Source files are unchanged.
- Archive creation is not rollback execution; rollback remains manual and requires explicit approval.

## Checkpoint Regeneration Plan (P4-M7)

Checkpoint regeneration produces a review plan when drift crosses the configured threshold.

- Plans stay `pending_review`.
- `regeneration_allowed_now` and `active_write_allowed` are always `false`.
- Saving a plan writes only to `alters/calibration/checkpoint_plans/`.
- No branch, alter, snapshot, or active YAML regeneration occurs.

## Phase 4 Closeout

Phase 4 closeout verifies the backend calibration loop scope:

- P4-M1R through P4-M7 are present.
- No provider, frontend, or database implementation is added.
- No active YAML or rubric diff is allowed.
- Raw runtime archives, checkpoint plans, and rubric suggestions are ignored unless they are explicit templates/placeholders.
- Phase 4 closeout seals the backend calibration loop candidate, not full productization.

## Run

```bash
pip install -e ".[dev]"
uvicorn alters_lab.main:app --reload
pytest
```
