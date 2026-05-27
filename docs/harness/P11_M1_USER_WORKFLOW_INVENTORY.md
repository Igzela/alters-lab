# P11-M1 User Workflow Inventory

## Workflow Definitions

| # | Workflow | Status | Evidence Source |
|---|----------|--------|-----------------|
| 1 | Install package | usable | P9 lifecycle smoke |
| 2 | Launch app | usable | P9 lifecycle smoke, CLI start/open |
| 3 | First run | usable | GettingStarted page + checklist |
| 4 | Provider disabled | usable | Default mode, no config needed |
| 5 | Provider mock setup | usable | ProviderSettings page end-to-end |
| 6 | Provider live setup | partial | Config/test works, no real provider tested |
| 7 | Weekly note ingest | usable | P10-M2 real use, frontend + API |
| 8 | Weekly review | usable | P10-M3 real use, 6-step flow |
| 9 | Action alignment score | usable | P10-M3 real use, score submission |
| 10 | Reality score / calibration loop | partial | Score submission works, no loop exercised |
| 11 | Alter dialogue | partial | UI exists, backend read-only, no real dialogue |
| 12 | Rubric delta | partial | API works, cold start, no real suggestions |
| 13 | Checkpoint plan | partial | API works, cold start, no real plans |
| 14 | Backup | usable | CLI backup with dry-run verified |
| 15 | Uninstall/remove | usable | P9 lifecycle smoke |
| 16 | P6 validation package | blocked_by_design | Intentionally blocked until app complete |

---

## Workflow 1: Install Package

- **Frontend path**: N/A (CLI + system package)
- **Backend APIs**: N/A
- **CLI dependency**: `dpkg -i alters-lab_*.deb`
- **Data records created/read**: config.yaml created on first run
- **Current status**: usable
- **Evidence source**: P9-M2 disposable install/upgrade/remove verification
- **Largest gap**: None
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 2: Launch App

- **Frontend path**: Auto-opens browser to http://127.0.0.1:18790
- **Backend APIs**: GET /health, GET /local-app/status
- **CLI dependency**: `alters-lab start` or `alters-lab open`
- **Data records created/read**: PID file written to state_dir
- **Current status**: usable
- **Evidence source**: P9-M2 lifecycle verification, P7-M3 CLI launcher
- **Largest gap**: None
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 3: First Run

- **Frontend path**: GettingStarted page (nav: "Getting Started")
- **Backend APIs**: GET /product/status, GET /runtime-layout/status
- **CLI dependency**: None
- **Data records created/read**: config.yaml, secrets.yaml created
- **Current status**: usable
- **Evidence source**: P9-M3 first-run onboarding guide
- **Largest gap**: Checklist is static; no interactive guidance
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 4: Provider Disabled

- **Frontend path**: ProviderSettings page shows "disabled" mode
- **Backend APIs**: GET /provider-config/status
- **CLI dependency**: None
- **Data records created/read**: config.yaml (provider.mode = "disabled")
- **Current status**: usable
- **Evidence source**: P8-M1 provider adapter contract
- **Largest gap**: None — this is the default safe mode
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 5: Provider Mock Setup

- **Frontend path**: ProviderSettings page — select "mock" mode, test connectivity
- **Backend APIs**: POST /provider-config/config, POST /provider-config/test, GET /provider-config/status
- **CLI dependency**: None
- **Data records created/read**: config.yaml updated, secrets.yaml (if key stored)
- **Current status**: usable
- **Evidence source**: P8-M2 connectivity check, P8-M5 E2E smoke
- **Largest gap**: None
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 6: Provider Live Setup

- **Frontend path**: ProviderSettings page — select "openai_compatible" mode, enter base URL + key, test
- **Backend APIs**: POST /provider-config/config, POST /provider-config/secret, POST /provider-config/test, POST /provider-connectivity/check
- **CLI dependency**: None
- **Data records created/read**: config.yaml, secrets.yaml
- **Current status**: partial
- **Evidence source**: P8-M1 adapter contract, P8 provider safety audit
- **Largest gap**: No real provider tested end-to-end in production. Config/test works but no live generation verified.
- **Blocks normal daily use**: No (mock works fine)
- **Blocks P6 validation start**: No (mock is acceptable for validation)

## Workflow 7: Weekly Note Ingest

- **Frontend path**: WeeklyReview page — Step 1: paste raw note, click ingest
- **Backend APIs**: POST /obsidian-weekly-note/ingest, GET /obsidian-weekly-note/list
- **CLI dependency**: None
- **Data records created/read**: Creates YAML in weekly_notes/ area
- **Current status**: usable
- **Evidence source**: P10-M2 first real weekly note ingested
- **Largest gap**: F-001 React textarea sync (low severity, accepted_no_fix)
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 8: Weekly Review

- **Frontend path**: WeeklyReview page — Steps 2-5: start review → review content → complete → score
- **Backend APIs**: POST /weekly-review/start, GET /weekly-review/list, POST /weekly-review/{session_id}/complete, POST /action-alignment/score
- **CLI dependency**: None
- **Data records created/read**: Creates YAML in weekly_reviews/ area, creates score in calibration_records/
- **Current status**: usable
- **Evidence source**: P10-M3 first real weekly review completed, action alignment score 0.75
- **Largest gap**: F-002 section validation strictness (low severity, accepted_no_fix)
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 9: Action Alignment Score

- **Frontend path**: WeeklyReview page — Step 5: submit scores (direction_alignment, execution_consistency, avoidance_level)
- **Backend APIs**: POST /action-alignment/score, GET /action-alignment/list, GET /action-alignment/{score_id}
- **CLI dependency**: None
- **Data records created/read**: Creates YAML in calibration_records/ area
- **Current status**: usable
- **Evidence source**: P10-M3 real score submitted (0.75)
- **Largest gap**: None — works end-to-end
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 10: Reality Score / Calibration Loop

- **Frontend path**: RealityScore page — submit reality score form
- **Backend APIs**: POST /calibration-loop/reality-scores, POST /calibration-loop/drift/calculate, GET /calibration-loop/history
- **CLI dependency**: None
- **Data records created/read**: Writes to calibration_records/, reads history
- **Current status**: partial
- **Evidence source**: P4-M2 reality score form exists, P8 backend tests
- **Largest gap**: Score submission works but no real calibration loop exercised end-to-end. No drift calculation triggered by real data. History page shows empty in cold start.
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 11: Alter Dialogue

- **Frontend path**: AlterDialogue page — select alter, view context, send prompt
- **Backend APIs**: GET /alter-dialogue/alters, GET /alter-dialogue/{alter_id}/context, POST /alter-dialogue/{alter_id}/reply
- **CLI dependency**: None
- **Data records created/read**: Reads alter YAML, no new records created
- **Current status**: partial
- **Evidence source**: P4-M1 dialogue runtime, P8-M3 dialogue preview
- **Largest gap**: Backend is read-only context + reply. No real provider dialogue flow exercised. UI exists but no conversation history persistence.
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 12: Rubric Delta

- **Frontend path**: RubricDelta page — click suggest, view result
- **Backend APIs**: POST /rubric-delta/suggest, GET /rubric-delta/list
- **CLI dependency**: None
- **Data records created/read**: Writes to rubric delta area, reads list
- **Current status**: partial
- **Evidence source**: P4-M5 rubric delta suggestion API
- **Largest gap**: Cold start — no real suggestions exist. Suggest works but returns empty in fresh install.
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 13: Checkpoint Plan

- **Frontend path**: CheckpointPlan page — click plan, view result
- **Backend APIs**: POST /checkpoint-regeneration/plan, GET /checkpoint-regeneration/list
- **CLI dependency**: None
- **Data records created/read**: Writes plan to checkpoint area, reads list
- **Current status**: partial
- **Evidence source**: P4-M7 checkpoint regeneration plan
- **Largest gap**: Cold start — no real plans exist. Plan generation works but returns empty in fresh install.
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 14: Backup

- **Frontend path**: N/A (CLI only)
- **Backend APIs**: None (CLI uses services directly)
- **CLI dependency**: `alters-lab backup --dry-run` or `alters-lab backup`
- **Data records created/read**: Reads all product data, creates tar.gz export
- **Current status**: usable
- **Evidence source**: P9-M2 lifecycle verification, P7-M7 upgrade/uninstall/data safety
- **Largest gap**: None — backup works with dry-run and full modes
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 15: Uninstall / Remove

- **Frontend path**: N/A (system package)
- **Backend APIs**: N/A
- **CLI dependency**: `dpkg -r alters-lab`
- **Data records created/read**: Preserves user data in ~/.local/share/alters-lab/
- **Current status**: usable
- **Evidence source**: P9-M2 disposable install/upgrade/remove verification
- **Largest gap**: None
- **Blocks normal daily use**: No
- **Blocks P6 validation start**: No

## Workflow 16: P6 Validation Package

- **Frontend path**: N/A (blocked by design)
- **Backend APIs**: /behavior-validation/*, /p6-data-retention/*, /p6-provider-policy/*
- **CLI dependency**: None
- **Data records created/read**: N/A
- **Current status**: blocked_by_design
- **Evidence source**: P10-M5 decision gate — blocked by product incompleteness
- **Largest gap**: Intentionally blocked. App must be functionally complete before P6 validation starts.
- **Blocks normal daily use**: No (intentional)
- **Blocks P6 validation start**: Yes (by design)

---

## Workflow Gap Summary

### Fully Usable (8 workflows)
Install, launch, first run, provider disabled, provider mock, weekly note ingest, weekly review, action alignment score, backup, uninstall

### Partial (5 workflows)
Provider live setup, reality score/calibration loop, alter dialogue, rubric delta, checkpoint plan

### Blocked by Design (1 workflow)
P6 validation package

### Critical Gaps for Normal Daily Use
None — the core weekly review workflow (ingest → review → score) works end-to-end.

### Critical Gaps for P6 Validation
None from a workflow perspective — P6 validation is blocked by product completeness (P11 purpose), not by specific workflow failures.
