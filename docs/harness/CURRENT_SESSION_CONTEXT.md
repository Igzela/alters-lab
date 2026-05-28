# Current Session Context

Last updated: 2026-05-28

## Project State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P7-R1 (frontend Weekly Review usability) complete
- P6: `CODE_COMPLETE / VALIDATION_PAUSED_FOR_PRODUCT_CHANGE / NOT_SEALED`
- P8: sealed as `REAL_PROVIDER_READY_LOCAL_APP`
- P8 all milestones done (P8-000 through P8-M7)
- P8 provider safety audit: 7 sections all PASS
- P9: sealed (P9-000 through P9-M7 all done)
- P10: P10-000 through P10-M6 done; P10-M7 blocked
- P11: P11-000 through P11-M7 done — **P11 sealed as PRODUCT_COMPLETE_BEFORE_VALIDATION**
- P12: Owner override — UI improvements during validation window. P12-000 done. P12-M1 (Tailwind) done. P12-M2 (Loading/Error) done. P12-M3 (i18n) done. P12-M4 (Onboarding) ready_with_approval. P12-M5-M7 blocked.

## Current State

- P12-000: done (owner override plan, P6 validation paused for product change)
- P6: CODE_COMPLETE / VALIDATION_PAUSED_FOR_PRODUCT_CHANGE / NOT_SEALED
- P6 validation paused: 2026-05-28 (owner override for UI improvements)
- Week 1 evidence preserved but not counted by default
- P12-M1: done (Tailwind visual baseline, all 13 pages converted, build passes)
- P12-M2: done (Loading/Error system, 2 shared components, 8 pages updated)
- P12-M3: done (i18n zh/en toggle, react-i18next, 15 pages/components updated, en/zh locale files, localStorage persistence)
- P12-M4: ready_with_approval (New-user guided path)
- P12-M5 through P12-M7: blocked
- P10-M7: blocked

## Next Task

P12-M4: New-user guided path
1. Add onboarding flow for new users
2. Guide through first steps (provider, weekly review, etc.)
3. No GSAP yet (deferred to P12-M5)

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
- P12 scope: frontend UI changes only (Tailwind, GSAP, i18n, loading states, onboarding)
- P12 not allowed: backend behavior changes, provider changes, active YAML mutation, real provider calls

## Documentation Maintenance

Before committing, update the handoff docs if status, tests, commands, boundaries, workflows, routes, pages, evidence, or next steps changed. At minimum check `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/harness/START_HERE_FOR_NEW_SESSION.md`, this file, `docs/harness/PROJECT_BOARD.md`, `docs/harness/TASK_QUEUE.md`, `docs/harness/RUN_LOG.md`, and `docs/harness/EVIDENCE_INDEX.md`.
