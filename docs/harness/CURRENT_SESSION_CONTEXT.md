# Current Session Context

Last updated: 2026-05-27

## Project State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P7-R1 (frontend Weekly Review usability) complete
- P6: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`
- P8: sealed as `REAL_PROVIDER_READY_LOCAL_APP`
- P8 all milestones done (P8-000 through P8-M7)
- P8 provider safety audit: 7 sections all PASS
- P9-000 done (release hygiene boundary plan)
- P9-M1 ready_with_approval (install docs)
- P9-M2 through P9-M7 blocked

## What Was Just Completed

P9-000: Release Hygiene & Install Readiness Boundary Plan.
- Created P9 plan, taskbook, release readiness boundary, user-facing docs plan
- Defined threat model (7 threats), success standard (7 criteria), milestone table (P9-000 through P9-M7)
- Hard boundaries: no alters/current changes, no rubric changes, no runtime records, no secrets, no real provider calls, no P6 claims, no P6 seal
- Updated 8 governance docs (PROJECT_BOARD, TASK_QUEUE, DECISION_RECORD, RISK_REGISTER, RUN_LOG, EVIDENCE_INDEX, START_HERE, CURRENT_SESSION_CONTEXT)
- No code changes, no active YAML/rubric changes

## Next Decision

P9-000 is done. Options:
1. Begin P9-M1 (install docs) after explicit approval
2. Begin real P6 validation later
3. Other product work

New sessions must not claim P6 validated.
New sessions must not start P9-M1 without explicit approval.

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
- No P9-M1 start without explicit approval
- No live provider calls without explicit configuration
