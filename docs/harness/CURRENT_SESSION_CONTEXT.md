# Current Session Context

Last updated: 2026-05-27

## Project State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P7-R1 (frontend Weekly Review usability) complete
- P6: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`
- P8-000: done (boundary plan created)
- P8-M1: done (provider adapter contract hardened)
- P8-M2: done (connectivity check with /models endpoint, exact confirmation gating)
- P8-M3: done (provider-backed dialogue preview with /chat/completions, injectable http_client)
- P8-M4: done (weekly review assistant mode, reuses provider_dialogue_preview)
- P8-M5: done (E2E product validation smoke, package-context isolated HOME)
- P8-M6: ready_with_approval (Provider Safety Audit)
- P8-M7: blocked
- No active phase in progress

## What Was Just Completed

P8-M5: E2E Product Validation.
- Created tools/p8_e2e_product_smoke.py for package-context isolated HOME smoke
- Validates all P8 provider paths: adapter, connectivity, dialogue preview, weekly assistant
- Validates weekly review flow with assistant suggestion
- Validates backup/data safety
- Package build, P7 smoke, P8 smoke all PASS
- 15 new tests, 1173 total backend tests passing
- P8-M6 ready_with_approval

## Next Decision

P8-M6 (Provider Safety Audit) is ready_with_approval.
Requires explicit human/GPT approval before starting.

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

# Git status
git status
```

## Key Boundaries

- No `alters/current/**` changes without approval
- No runtime records committed
- No P6 validation claims
- No P8 restart without approval
- No live provider calls without explicit configuration
