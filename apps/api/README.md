# Alters Lab API

FastAPI backend for the Alters Lab personal future-branch simulation system.

## Overview

Provides local FastAPI runtime services, built-frontend serving, controlled YAML workflows, and local provider configuration boundaries. No database, cloud service, or default live LLM provider call is required.

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
| GET | `/runtime-layout/health` | Runtime layout component health |
| GET | `/runtime-layout/status` | Resolved dev/packaged layout status with secrets redacted |
| POST | `/runtime-layout/ensure-config` | Create user config only; no secrets or runtime records |
| GET | `/local-app/health` | Unified local app server health |
| GET | `/local-app/status` | Local app status, runtime mode, frontend availability, and safety flags |
| GET | `/local-app/frontend-status` | Built frontend dist availability and path |
| GET | `/provider-config/health` | Local provider configuration health |
| GET | `/provider-config/status` | Redacted provider configuration status |
| GET | `/provider-config/config` | Non-secret provider configuration |
| POST | `/provider-config/config` | Update non-secret provider settings |
| POST | `/provider-config/secret` | Store provider API key in local secret storage |
| DELETE | `/provider-config/secret` | Delete provider API key from local secret storage |
| POST | `/provider-config/test` | Dry-run provider configuration check; no live provider call |

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
- **runtime_layout** — P7 dev/packaged runtime path resolver and config helpers; packaged mode targets user data dirs
- **local_app** — P7 unified local server status and built frontend static serving through FastAPI
- **provider_config** — P7 local provider configuration, redacted status, and local secret storage; no provider calls

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

## Runtime Layout (P7-M1)

Runtime layout provides the path boundary needed for packaging.

- **Dev mode** remains repo-compatible and preserves existing `tmp_path` test behavior.
- **Packaged mode** writes runtime records under `~/.local/share/alters-lab/product/`.
- Config resolves to `~/.config/alters-lab/config.yaml`.
- Logs resolve to `~/.local/state/alters-lab/logs/`.
- Provider secrets are not written by this slice; fallback path is `~/.config/alters-lab/secrets.yaml` with `0600` when explicitly created.
- `/runtime-layout/status` redacts secret state and does not create files.
- `/runtime-layout/ensure-config` creates config only and does not write runtime records, active YAML, rubric, or secrets.

## Unified Local Server (P7-M2)

FastAPI now serves API routes and built React frontend assets from one process.

- Dev frontend dist resolves to `apps/web/dist`.
- Packaged frontend dist resolves to `<app_root>/web/dist`, for example `/opt/alters-lab/web/dist`.
- `/local-app/status` reports backend readiness, frontend availability, runtime mode, provider mode, redacted secrets, and P6 safety state.
- `/` serves `index.html` when frontend dist exists.
- `/assets/*` serves files only from frontend dist assets.
- SPA fallback serves frontend routes but blocks known API prefixes.
- Missing frontend dist does not crash API; `/` returns a clear placeholder with 503.
- Existing API routes remain registered before frontend fallback.

## Local Launcher (P7-M3)

The local launcher controls one FastAPI process without Codex, Claude Code, curl, pytest, or manual uvicorn commands.

Commands:

- `alters-lab start`
- `alters-lab stop`
- `alters-lab status`
- `alters-lab open`
- `alters-lab doctor`

Module form for development:

```bash
PYTHONPATH=apps/api/src python3 -m alters_lab.cli status --mode dev --json
PYTHONPATH=apps/api/src python3 -m alters_lab.cli doctor --mode dev --json
PYTHONPATH=apps/api/src python3 -m alters_lab.cli start --mode dev --dry-run --json
PYTHONPATH=apps/api/src python3 -m alters_lab.cli stop --mode dev --json
```

Launcher behavior:

- Defaults to `127.0.0.1:18790`.
- Starts `python -m uvicorn alters_lab.main:app`.
- Writes PID file under runtime state dir.
- Writes logs under runtime logs dir.
- `open` starts the server unless `--no-start` is supplied.
- `doctor` reports PASS/WARN/BLOCKED checks without writing runtime records.

## Provider Configuration (P7-M4)

Local provider configuration is available through `/provider-config/*` and the frontend Provider page.

- Default mode is `disabled`.
- Supported modes are `disabled`, `mock`, and `openai-compatible-http`.
- Real provider mode requires `explicit_user_configuration=true`.
- `/provider-config/config` writes only non-secret config.
- `/provider-config/secret` stores keys in optional keyring storage or `secrets_yaml_fallback`.
- Fallback secrets are written to `secrets.yaml` with mode `0600`.
- API responses never return the provider API key.
- `/provider-config/test` is dry-run by default and does not make network calls.
- Provider output cannot write active YAML, persist by default, or generate reality scores.
- P6 remains not behavior validated and not sealed.

## Debian Package Build (P7-M5)

Build the local package candidate from repo root:

```bash
python tools/build_deb.py
```

The build stages files under `build/deb/alters-lab` and writes `dist/deb/alters-lab_0.1.0_amd64.deb`. The package installs app code under `/opt/alters-lab`, the built frontend under `/opt/alters-lab/web/dist`, a bundled Python venv under `/opt/alters-lab/.venv`, and the launcher at `/usr/bin/alters-lab`.

The package does not include user config, secrets, logs, raw P6 runtime records, `node_modules`, or `.env` files. Generated `.deb` artifacts remain ignored by git.
- P6 behavior validation and seal state remain false.

## Run

```bash
pip install -e ".[dev]"
uvicorn alters_lab.main:app --reload
pytest
```
