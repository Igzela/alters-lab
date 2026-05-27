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
- P9-M2 ready_with_approval (disposable verification)
- P9-M3 through P9-M7 blocked

## What Was Just Completed

P9-M1: User-facing install/launch/uninstall docs.
- Created docs/user/INSTALL.md — system requirements, install from .deb, build from source, installed paths, data paths, verification
- Created docs/user/FIRST_RUN.md — launch, what is Alters Lab, provider mode, smoke test, P6/P7/P8 explanation, weekly review, stopping
- Created docs/user/UNINSTALL.md — stop, remove, what's removed/preserved, full cleanup, reinstall, upgrade
- Created docs/user/DATA_AND_BACKUP.md — data paths, backup command, options, restore, data safety, P6 runtime records
- Updated 8 governance docs
- No code changes, no active YAML/rubric changes

## Next Decision

P9-M1 is done. Options:
1. Begin P9-M2 (disposable install/upgrade/remove verification) after explicit approval
2. Begin real P6 validation later
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
- No P9-M1 start without explicit approval
- No live provider calls without explicit configuration
