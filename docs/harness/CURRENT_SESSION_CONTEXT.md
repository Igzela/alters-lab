# Current Session Context

Last updated: 2026-05-28

## Project State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P7-R1 (frontend Weekly Review usability) complete
- P6: `CODE_COMPLETE_VALIDATION_RESTARTED / NOT_VALIDATED / NOT_SEALED`
- P8: sealed as `REAL_PROVIDER_READY_LOCAL_APP`
- P8 all milestones done (P8-000 through P8-M7)
- P8 provider safety audit: 7 sections all PASS
- P9: sealed (P9-000 through P9-M7 all done)
- P10: P10-000 through P10-M6 done; P10-M7 blocked
- P11: P11-000 through P11-M7 done — **P11 sealed as PRODUCT_COMPLETE_BEFORE_VALIDATION**
- P12: Owner override — UI improvements during validation window. P12-000 done. P12-M1 (Tailwind) done. P12-M2 (Loading/Error) done. P12-M3 (i18n) done. P12-M4 (Onboarding) ready_with_approval. P12-M5-M7 blocked.

## Current State

- P12-000: done (owner override plan, P6 validation paused for product change)
- P6: CODE_COMPLETE_VALIDATION_RESTARTED / NOT_VALIDATED / NOT_SEALED
- P6 validation restarted from zero: 2026-05-28 (P12-M7 decision)
- Week 1 evidence archived as historical (pre-P12), not counted
- Fresh P6 evidence collection may now begin (P13 COMPLETE)
- P12-M1: done (Tailwind visual baseline, all 13 pages converted, build passes)
- P12-M2: done (Loading/Error system, 2 shared components, 8 pages updated)
- P12-M3: done (i18n zh/en toggle, react-i18next, 15 pages/components updated, en/zh locale files, localStorage persistence)
- P12-M4: done (New-user guided path, step-by-step wizard with progress bar)
- P12-M5: done (GSAP motion layer, lightweight animations)
- P12-M6: done (Product smoke and real-use pilot — P8 smoke PASS, browser verification PASS)
- P12-M7: done (P6 validation restart — restarted from zero, Week 1 evidence archived as historical)
- P12 scope: COMPLETE (M1-M7 all done)
- P10-M7: blocked
- P13-000: done (UX hardening plan)
- P13-M1: done (interaction integrity + accessibility baseline)
- P13-M2: done (i18n completion + localized formatting)
- P13-M3: done (design token and component baseline)
- P13-M4: done (toast notification system)
- P13-M5: done (motion polish)
- P13-M6: done (product smoke and governance closeout — GPT PASS_WITH_GOVERNANCE_CLOSEOUT)
- P13 scope: COMPLETE (M1-M6 all done)
- P14-000: done (frontend polish plan)
- P14-M1: done (component standardization and date formatting)
- P14-M1-R1: done (fix date i18n — pass language explicitly)
- P14-M2: done (styled range inputs, select dark mode, session type i18n)
- P14-M3: done (WeeklyReview step progress bar)
- P14-M4: done (style JSON display blocks)
- P14-M5: done (skip-to-content link)
- P14-M6: done (AlterDialogue labels, BehaviorValidation i18n, DataManagement toasts)
- P14-M7: done (ProviderSettings toast notifications)
- P14-M8: done (Alter labels i18n)
- P14-FINAL-CLOSEOUT-E1: done (close frontend polish after M8 — GPT PASS)
- P14 scope: COMPLETE (M1-M8 + R1 all done)

## Next Task

Fresh post-P14 P6 evidence collection may begin. Run weekly reviews to collect evidence (4 weekly reviews + 4 calibration records + 1 pattern review across 21+ days).
- P14 scope COMPLETE (GPT PASS — BLOCKED_WITH_SMALL_R1 resolved)
- Collect fresh P6 evidence: 4 weekly reviews + 4 calibration records + 1 pattern review across 21+ days
- P6 behavior validation available via POST /behavior-validation/evaluate
- P6 closeout available via GET /phase6-closeout/report

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
- P13 scope: UX hardening only (interaction integrity, i18n completion, design tokens, toast system, motion polish)
- P13 not allowed: backend behavior changes, provider changes, active YAML mutation, real provider calls
- Fresh P6 evidence collection may now begin (P13 COMPLETE)

## Documentation Maintenance

Before committing, update the handoff docs if status, tests, commands, boundaries, workflows, routes, pages, evidence, or next steps changed. At minimum check `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/harness/START_HERE_FOR_NEW_SESSION.md`, this file, `docs/harness/PROJECT_BOARD.md`, `docs/harness/TASK_QUEUE.md`, `docs/harness/RUN_LOG.md`, and `docs/harness/EVIDENCE_INDEX.md`.
