# Start Here for New Session

Read this file first in any new ChatGPT, Codex, or Claude session.

## What is Alters Lab?

Personal future path simulation and calibration system. Not a content creation tool.

## Current State (as of 2026-05-27)

- **P7**: Sealed as `LOCAL_APP_RELEASE_CANDIDATE`. Debian package builds, frontend works, CLI launcher works.
- **P7-R1**: Frontend Weekly Review usability layer complete. All 6 steps wired, P6Progress panel showing P6 state with false flags.
- **P6**: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`. Human decision to skip 4-week real-use validation. P6 code-complete accepted as-is.
- **P8**: Sealed as `REAL_PROVIDER_READY_LOCAL_APP`. All milestones done. 1215 backend tests passing.
- **P8 provider safety**: 7-section audit all PASS (grep scan, route audit, live constants, schema safety, evidence contract, secret policy, mutation boundary).
- **P9**: P9-000 done (release hygiene boundary plan). P9-M1 ready_with_approval (install docs). Rest blocked. Do not start P9-M1 without explicit approval.
- **P6 validation**: Parked. No behavior validation started. No seal claim. No 4-week window.

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
