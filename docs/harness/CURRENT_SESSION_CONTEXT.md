# Current Session Context

Last updated: 2026-05-27

## Project State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P7-R1 (frontend Weekly Review usability) complete
- P6: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`
- P8: sealed as `REAL_PROVIDER_READY_LOCAL_APP`
- P8 all milestones done (P8-000 through P8-M7)
- P8 provider safety audit: 7 sections all PASS
- P9: sealed (P9-000 through P9-M7 all done)
- P10: P10-000 done (Personal Pilot & Real-Use Cutover Boundary Plan)
- P10-M1: ready_with_approval (Local installation cutover checklist)

## What Was Just Completed

P10-000: Personal Pilot & Real-Use Cutover Boundary Plan.
- Created P10_000_PERSONAL_PILOT_AND_REAL_USE_CUTOVER_PLAN.md
- Created P10_TASKBOOK.md, P10_REAL_USE_BOUNDARY.md, P10_P6_VALIDATION_BRIDGE.md, P10_PILOT_EVIDENCE_REQUIREMENTS.md
- Updated PROJECT_BOARD, TASK_QUEUE, DECISION_RECORD, RISK_REGISTER, RUN_LOG, EVIDENCE_INDEX, START_HERE_FOR_NEW_SESSION, CURRENT_SESSION_CONTEXT
- P10 defines: operational cutover, evidence discipline, friction discovery, P6 validation bridge
- P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED

## Next Decision

P10-000 is done. Next step:
1. P10-M1: Local installation cutover checklist (ready_with_approval)
2. P10-M2 through P10-M7: blocked

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
