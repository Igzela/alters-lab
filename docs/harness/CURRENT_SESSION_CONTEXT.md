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
- P9-M1 done (install/launch/uninstall docs)
- P9-M2 done (disposable dpkg lifecycle verification)
- P9-M3 done (first-run onboarding guide + Getting Started frontend page)
- P9-M4 done (provider setup and safety guide + ProviderSettings safety notes)
- P9-M7 done (P9 Closeout)
- P9 sealed

## What Was Just Completed

P9-M7: P9 Closeout.
- Created docs/harness/P9_CLOSEOUT_REPORT.md
- All 7 milestones done, all 7 success criteria PASS
- 1270 backend tests, frontend PASS, package PASS, lifecycle smoke PASS
- No forbidden claims, no secrets, no version bump (docs/governance only)
- P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED

## Next Decision

P9 is sealed. Options:
1. Start P10 (if planned) after explicit approval
2. Real P6 validation using the local app
3. Other product work

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
