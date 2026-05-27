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
- P10-M1: done (Local installation cutover checklist + evidence template)

## What Was Just Completed

P10-M2: First real weekly note ingest instructions + evidence template.
- Created P10_M2_FIRST_REAL_WEEKLY_NOTE_INGEST.md (operator instructions)
- Created P10_M2_REAL_WEEKLY_NOTE_EVIDENCE_TEMPLATE.md (fillable redacted YAML template)
- P10-M2 is ready_for_human_execution — Charlie must perform the actual local app operation
- P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED

## Next Decision

P10-M2 instructions ready. Charlie must:
1. Use packaged app to ingest a real weekly note
2. Fill in the evidence template with redacted summary
3. Confirm completion

After Charlie confirms, mark P10-M2 done and proceed to P10-M3.

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
