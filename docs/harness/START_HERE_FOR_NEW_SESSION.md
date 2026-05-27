# Start Here for New Session

Read this file first in any new ChatGPT, Codex, or Claude session.

## What is Alters Lab?

Personal future path simulation and calibration system. Not a content creation tool.

## Current State (as of 2026-05-27)

- **P7**: Sealed as `LOCAL_APP_RELEASE_CANDIDATE`. Debian package builds, frontend works, CLI launcher works.
- **P7-R1**: Frontend Weekly Review usability layer complete. All 6 steps wired, P6Progress panel showing P6 state with false flags.
- **P6**: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`. Real-use validation has not started. P6 validation requires explicit human/GPT decision.
- **P8**: Sealed as `REAL_PROVIDER_READY_LOCAL_APP`. All milestones done. 1215 backend tests passing.
- **P8 provider safety**: 7-section audit all PASS (grep scan, route audit, live constants, schema safety, evidence contract, secret policy, mutation boundary).
- **P9**: All milestones done (P9-000 through P9-M7). P9 closeout PASS. Install docs, lifecycle verification, onboarding guide, provider guide, troubleshooting/doctor, release checklist, version bump policy all complete. Closeout report: `docs/harness/P9_CLOSEOUT_REPORT.md`.
- **P10**: Personal Pilot & Real-Use Cutover phase. P10-000 done. P10-M1 done. P10-M2 done (first real weekly note ingested). P10-M3 done (first real weekly review session completed, action alignment score 0.75). P10-M4 done (friction log: 0 blocker friction, 3 low-severity accepted_no_fix). P10-M5 awaiting_human_decision (GPT recommends START_P6_VALIDATION_NOW, awaiting Charlie's explicit decision).
- **P6 validation**: Not started. Starts after explicit human/GPT decision. Completes after 4 real weekly reviews, 21 days.

## Reading Order

1. `docs/harness/PROJECT_BOARD.md` — task states and phase status
2. `docs/harness/TASK_QUEUE.md` — full task history with notes
3. `docs/harness/P7_CLOSEOUT_REPORT.md` — what P7 sealed and why
4. `docs/harness/P7_FRONTEND_USABILITY_R1.md` — what P7-R1 added
5. `docs/harness/CURRENT_SESSION_CONTEXT.md` — what to do next

## What NOT to Do

- Do not start P8 without explicit human/GPT approval.
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
