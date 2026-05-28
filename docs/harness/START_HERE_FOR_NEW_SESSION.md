# Start Here for New Session

Read this file first in any new ChatGPT, Codex, or Claude session.

## What is Alters Lab?

Personal future path simulation and calibration system. Not a content creation tool.

## Current State (as of 2026-05-28)

- **P7**: Sealed as `LOCAL_APP_RELEASE_CANDIDATE`. Debian package builds, frontend works, CLI launcher works.
- **P7-R1**: Frontend Weekly Review usability layer complete. All 6 steps wired, P6Progress panel showing P6 state with false flags.
- **P6**: `CODE_COMPLETE / VALIDATION_PAUSED_FOR_PRODUCT_CHANGE / NOT_SEALED`. P6 validation paused for owner-requested UI improvements (P12). Week 1 evidence preserved but not counted by default.
- **P8**: Sealed as `REAL_PROVIDER_READY_LOCAL_APP`. All milestones done. 1215 backend tests passing.
- **P8 provider safety**: 7-section audit all PASS.
- **P9**: Sealed. Install docs, lifecycle verification, onboarding guide, provider guide, troubleshooting/doctor, release checklist, version bump policy all complete.
- **P10**: P10-000 through P10-M6 done. P10-M7 blocked.
- **P11**: Sealed as `PRODUCT_COMPLETE_BEFORE_VALIDATION`.
- **P11-PILOT-1**: PASS.
- **P12**: Owner override — UI improvements during validation window. P12-000 done. P12-M1 (Tailwind) done. P12-M2 (Loading/Error) done. P12-M3 (i18n) done. P12-M4 (Onboarding) done. P12-M5 (GSAP) done. P12-M6 (Product smoke) ready_with_approval. P12-M7 blocked.
- **P6 validation**: Paused. P12 scope: Tailwind (done), Loading/Error (done), i18n, GSAP, onboarding, product smoke. After P12-M6 (product smoke), P6 validation restart decision at P12-M7.

## Reading Order

1. `AGENTS.md` — cross-agent rules and documentation maintenance discipline
2. `CLAUDE.md` — Claude/GPT collaboration protocol and current technical context
3. `docs/harness/CURRENT_SESSION_CONTEXT.md` — latest state and next decision
4. `docs/harness/PROJECT_BOARD.md` — task states and phase status
5. `docs/harness/TASK_QUEUE.md` — full task history with notes
6. `docs/harness/P11_CLOSEOUT_REPORT.md` — what P11 sealed and why
7. `docs/runs/P11-PILOT-1-real-use-product-pilot.md` — latest real-use product pilot

## What NOT to Do

- Do not claim P6 validation or seal.
- Do not modify `alters/current/` active YAML without approval.
- Do not commit runtime records.
- Do not connect real LLM providers without explicit configuration.
- Do not add frontend, database, or provider output to active YAML.

## What You CAN Do

- Run backend tests: `PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q`
- Build frontend: `cd apps/web && npm run build`
- Build Debian package: `python3 tools/build_deb.py`
- Run P7 smoke: `python3 tools/p7_local_app_smoke.py --deb dist/deb/alters-lab_0.1.0_amd64.deb --json`
- Run P8 smoke: `python3 tools/p8_e2e_product_smoke.py --deb dist/deb/alters-lab_0.1.0_amd64.deb --json`
- Check git status: `git status`

## Documentation Maintenance

Before every commit-sized change, update the handoff docs if status, tests, commands, boundaries, workflows, routes, pages, evidence, or next steps changed:

- `docs/harness/START_HERE_FOR_NEW_SESSION.md`
- `docs/harness/CURRENT_SESSION_CONTEXT.md`
- `docs/harness/PROJECT_BOARD.md`
- `docs/harness/TASK_QUEUE.md`
- `docs/harness/RUN_LOG.md`
- `docs/harness/EVIDENCE_INDEX.md`
- `README.md`
- `CLAUDE.md`
- `AGENTS.md`

If no documentation update is needed, state why in the completion report.
