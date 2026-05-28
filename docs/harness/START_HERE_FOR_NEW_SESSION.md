# Start Here for New Session

Read this file first in any new ChatGPT, Codex, or Claude session.

## What is Alters Lab?

Personal future path simulation and calibration system. Not a content creation tool.

## Current State (as of 2026-05-28)

- **P7**: Sealed as `LOCAL_APP_RELEASE_CANDIDATE`. Debian package builds, frontend works, CLI launcher works.
- **P7-R1**: Frontend Weekly Review usability layer complete. All 6 steps wired, P6Progress panel showing P6 state with false flags.
- **P6**: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`. Real-use validation has not started. P6 validation requires explicit human/GPT decision.
- **P8**: Sealed as `REAL_PROVIDER_READY_LOCAL_APP`. All milestones done. 1215 backend tests passing.
- **P8 provider safety**: 7-section audit all PASS (grep scan, route audit, live constants, schema safety, evidence contract, secret policy, mutation boundary).
- **P9**: All milestones done (P9-000 through P9-M7). P9 closeout PASS. Install docs, lifecycle verification, onboarding guide, provider guide, troubleshooting/doctor, release checklist, version bump policy all complete. Closeout report: `docs/harness/P9_CLOSEOUT_REPORT.md`.
- **P10**: Personal Pilot & Real-Use Cutover phase. P10-000 done. P10-M1 done. P10-M2 done (first real weekly note ingested). P10-M3 done (first real weekly review session completed, action alignment score 0.75). P10-M4 done (friction log: 0 blocker friction, 3 low-severity accepted_no_fix). P10-M5 done — BLOCKED_BY_NEW_FRICTION (app not yet functionally complete for normal use). P10-M5-R2 done — reopened P6 validation start gate. P10-M5-R2-E1 done — Charlie chose START_P6_VALIDATION_NOW. P6 validation started 2026-05-28. P10-M6 done — Week 1 evidence committed (commit 14ee9d5). P10-M7 blocked.
- **P11**: Product Completeness Before Validation. P11-000 done. P11-M1 done (inventory). P11-M1-R1/R2/R3 done (granularity refinement, count fix, wording fix). P11-M2 done (workflow gap map: 23 workflows, 4 tiers, 20 gaps, 0 normal-use blockers, 4 P6 blockers). P11-M3 done (UX gaps: 12 gaps, 0 blockers, 3 medium, 9 low). P11-M4 done (gap closure plan: all frontend-only, existing APIs sufficient). P11-M5 done (CalibrationHistory detail/trend, RealityScore history, P6Progress rewrite, verdict explanations, dynamic alters). P11-M6 done (PatternReview, BehaviorValidation, DataManagement pages). P11-M7 done (product completeness smoke and closeout). **P11 sealed as PRODUCT_COMPLETE_BEFORE_VALIDATION**.
- **P11-PILOT-1**: Real-use product pilot PASS. All 10 visible workflows accessible and guarded; no hidden blockers observed.
- **P6 validation**: Started 2026-05-28. P6 state: `CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED`. P6 is NOT validated, NOT sealed. Week 1 evidence committed (14ee9d5). Completes after 4 real weekly reviews, 4 calibration records, 1 pattern review, 21 days / 4 ISO weeks. Prior pilot/smoke evidence does NOT count for completion.

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
