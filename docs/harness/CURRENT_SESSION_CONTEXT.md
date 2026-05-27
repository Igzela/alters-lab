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
- P10: P10-000 through P10-M5 done (BLOCKED_BY_NEW_FRICTION), P10-M6/M7 blocked
- P11: P11-000 done, P11-M1 done (inventory, R1/R2/R3), P11-M2 done (workflow gap map)

## What Was Just Completed

P11-M2: Missing core workflow map.
- 23 workflows classified into 4 tiers
- 20 gaps identified in gap matrix
- 0 normal-use blockers (core weekly review loop works)
- 4 P6-reconsideration blockers
- Priority: P11-M3 calibration/history visibility, P11-M4 validation readiness frontends
- Defer Phase 3-6 route frontends
- Created 3 files: MISSING_CORE_WORKFLOW_MAP.md, PRODUCT_COMPLETENESS_GAP_MATRIX.md, WORKFLOW_PRIORITY_DECISION.md

## Next Decision

P11-M3: UX gaps and normal-use blockers — ready_with_approval.
GPT must define UX gap analysis scope before Codex executes.
P11-M3 is analysis only — no implementation, no code changes.

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
