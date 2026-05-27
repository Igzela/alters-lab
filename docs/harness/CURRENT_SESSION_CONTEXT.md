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
- P9-M5 done (troubleshooting / doctor improvements + TROUBLESHOOTING.md)
- P9-M6 ready_with_approval
- P9-M7 blocked

## What Was Just Completed

P9-M5: Troubleshooting / doctor improvements.
- Enhanced build_doctor_report with new checks: app_root_exists, config_exists, product_data_dir_writable, state_dir_writable, provider_configured, secrets_file (0600 permissions), actionable WARN/BLOCKED messages
- Created docs/user/TROUBLESHOOTING.md (12 scenarios: app won't start, browser, port, command missing, frontend 503, provider issues, keyring, secrets perms, backup, uninstall data, P6, logs)
- Updated INSTALL.md, FIRST_RUN.md, DATA_AND_BACKUP.md, UNINSTALL.md, README.md with TROUBLESHOOTING links
- Added 10 new doctor tests (service + CLI)
- Updated 7 governance docs
- Backend tests passing
- Frontend build PASS

## Next Decision

P9-M5 is done. Options:
1. Begin P9-M6 (release artifact checklist and version bump policy) after explicit approval
2. Other product work

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
