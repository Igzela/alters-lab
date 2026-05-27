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
- P10: P10-000 done, P10-M1 done, P10-M2 done, P10-M3 done, P10-M4 ready_with_approval

## What Was Just Completed

P10-M3: First real weekly review session completed via packaged app API.
- Full workflow executed: note ingest → start review → complete review → action alignment score
- Action alignment score: 0.75 (aligned_progress)
- Evidence recorded in P10_M3_REAL_WEEKLY_REVIEW_EVIDENCE.md
- P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED

## Next Decision

P10-M4: Real-use friction log and fix triage — ready_with_approval.
GPT must review and approve before Charlie executes.

After P10-M4, proceed to P10-M5 (P6 validation start decision gate).

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
