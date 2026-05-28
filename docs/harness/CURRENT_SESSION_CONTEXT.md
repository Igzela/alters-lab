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
- P10: P10-000 through P10-M6 done; P10-M7 blocked
- P11: P11-000 through P11-M7 done — **P11 sealed as PRODUCT_COMPLETE_BEFORE_VALIDATION**

## Current State

- P11 sealed as PRODUCT_COMPLETE_BEFORE_VALIDATION (commit cb5b457)
- P11-PILOT-1: PASS (real-use product pilot)
- P10-M5-R2: done (START_P6_VALIDATION_NOW)
- P10-M5-R2-E1: done (decision recorded)
- P10-M6: done (Week 1 evidence committed, commit 14ee9d5)
- P6: CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED
- P6 validation started: 2026-05-28
- P6 is NOT validated, NOT sealed
- P10-M7: blocked

## Week 1 Validation Evidence

P10-M6 Week 1 operations completed:
- Weekly note ingested (session_type: project)
- Weekly review completed
- Action alignment score created (0.88, aligned_progress)
- Evidence file: docs/harness/P10_M6_WEEK1_VALIDATION_EVIDENCE.md
- Counters: 1 review, 1 calibration record, 0 pattern reviews, 0 days elapsed
- All boundaries maintained (no alters/current, no rubric, no secrets, no P6 claims)

## Next Task

Week 2 validation operations:
1. Ingest one real weekly note after 2026-05-28
2. Complete one real weekly review after 2026-05-28
3. Create one action alignment score after 2026-05-28
4. Provide redacted evidence for repo commit

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
