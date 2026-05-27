# Current Session Context

Last updated: 2026-05-28

## Project State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P7-R1 (frontend Weekly Review usability) complete
- P6: `CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED`
- P8: sealed as `REAL_PROVIDER_READY_LOCAL_APP`
- P8 all milestones done (P8-000 through P8-M7)
- P8 provider safety audit: 7 sections all PASS
- P9: sealed (P9-000 through P9-M7 all done)
- P10: P10-000 through P10-M5 done; P10-M5-R2 done (START_P6_VALIDATION_NOW); P10-M6 ready_with_approval; P10-M7 blocked
- P11: P11-000 through P11-M7 done — **P11 sealed as PRODUCT_COMPLETE_BEFORE_VALIDATION**

## Recent Product Pilot

P11-PILOT-1: Real-use product pilot.
- 10 workflows exercised end-to-end via Chrome DevTools MCP on packaged app (mode=mock)
- All workflows PASS: Status, Getting Started, Weekly Review, Dialogue, Reality Score, History, Patterns, Validation, Data, Provider
- Friction: none across all 10 workflows
- Boundary checks: PASS (no alters/current changes, no rubric changes, no runtime records committed, no secrets, no P6 claims)
- GPT verdict: PASS
- Report: docs/runs/P11-PILOT-1-real-use-product-pilot.md

## Current State

- P11 sealed as PRODUCT_COMPLETE_BEFORE_VALIDATION (commit cb5b457)
- P11-PILOT-1: PASS (real-use product pilot)
- P10-M5-R2: done (START_P6_VALIDATION_NOW)
- P10-M5-R2-E1: done (decision recorded)
- P6: CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED
- P6 validation started: 2026-05-28
- P6 is NOT validated, NOT sealed
- P10-M6: ready_with_approval

## Latest Gate Update

P10-M5-R2-E1: Recorded Charlie's START_P6_VALIDATION_NOW decision.
- Created evidence doc
- Updated 7 governance files
- P6 state: CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED
- Prior pilot/smoke evidence does NOT count for completion
- P10-M6 ready to define Week 1 validation package

## Next Task

P10-M6: Define Week 1 validation package — what to do this week, what local records count, what redacted evidence can be committed.

New sessions must not claim P6 validated.

## Verification Commands

```bash
# Backend tests
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q

# Frontend build
cd apps/web && npm run build

# Package build
python3 tools/build_deb.py

# P7 smoke
python3 tools/p7_local_app_smoke.py --deb dist/deb/alters-lab_0.1.0_amd64.deb --json

# P8 smoke
python3 tools/p8_e2e_product_smoke.py --deb dist/deb/alters-lab_0.1.0_amd64.deb --json

# Provider safety audit
python3 tools/p8_provider_safety_audit.py --json

# Git status
git status
```

## Key Boundaries

- No `alters/current/**` changes without approval
- No `alters/calibration/rubric.yaml` changes
- No runtime records committed
- No P6 validation claims
- No live provider calls without explicit configuration

## Documentation Maintenance

Before committing, update the handoff docs if status, tests, commands, boundaries, workflows, routes, pages, evidence, or next steps changed. At minimum check `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/harness/START_HERE_FOR_NEW_SESSION.md`, this file, `docs/harness/PROJECT_BOARD.md`, `docs/harness/TASK_QUEUE.md`, `docs/harness/RUN_LOG.md`, and `docs/harness/EVIDENCE_INDEX.md`.
