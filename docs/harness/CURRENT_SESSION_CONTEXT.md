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

P11-M1-R1: Inventory granularity refinement.
- Created P11_M1_DATA_RECORD_INVENTORY.md (19 record types, 12 P6 runtime areas)
- Created P11_M1_ROUTE_AND_PAGE_INVENTORY.md (124 routes, per-route method/path/RW/provider-risk/frontend-used/status)
- Created P11_M1_USER_WORKFLOW_INVENTORY.md (16 workflows with detail)
- Corrected overclaim: "130+ routes all functional" → "124 routes exist; readiness varies"
- Updated original inventory with data record section
- 8 governance files updated

## Next Decision

P11-M2: Missing core workflow map — ready_with_approval.
GPT must define what workflows to map before Codex executes.

After P11-M7 (product completeness smoke and closeout), revisit P6 validation start decision.

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
