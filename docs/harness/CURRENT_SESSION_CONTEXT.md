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
- P9-M3 ready_with_approval (first-run onboarding guide)
- P9-M4 through P9-M7 blocked

## What Was Just Completed

P9-M2: Disposable dpkg lifecycle verification.
- Created tools/p9_package_lifecycle_smoke.py — actual dpkg install/upgrade/remove in disposable fakeroot
- Uses --instdir/--admindir/--force-not-root/--force-script-chrootless/--force-depends
- 25 tests in apps/api/tests/test_p9_package_lifecycle_smoke.py
- 1240 backend tests passing
- Lifecycle smoke PASS: install places files, upgrade preserves user data, remove preserves secrets
- No host mutation, no provider calls, p6 flags false, method_is_extract_only false
- Created docs/harness/P9_M2_DISPOSABLE_INSTALL_VERIFICATION.md
- Updated 8 governance docs

## Next Decision

P9-M2 is done. Options:
1. Begin P9-M3 (first-run onboarding guide) after explicit approval
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
