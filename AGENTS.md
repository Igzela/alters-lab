# Agent Instructions

This repository is Alters Lab, a local personal future-path simulation and calibration tool.

## New Session Bootstrap

Every Codex, Claude Code, or other coding-agent session must start by reading:

1. `CLAUDE.md`
2. `docs/harness/START_HERE_FOR_NEW_SESSION.md`
3. `docs/harness/CURRENT_SESSION_CONTEXT.md`
4. `docs/harness/PROJECT_BOARD.md`
5. `docs/harness/TASK_QUEUE.md`

Those files are the handoff surface. If they disagree with each other, `README.md`, or recent git history, repair the documentation before continuing feature work.

## Current State

- P0-P11 are complete.
- P11 is sealed as `PRODUCT_COMPLETE_BEFORE_VALIDATION`.
- P6 remains `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`.
- Product is usable as a local personal tool, but P6 behavior validation still requires an explicit human/GPT start decision and a real-use window.
- P10-M5-R2 has reopened the P6 validation start gate and is awaiting Charlie's explicit decision: `START_P6_VALIDATION_NOW`, `RUN_ONE_MORE_PILOT_PASS`, `DEFER_P6_VALIDATION`, or `BLOCKED_BY_NEW_FRICTION`.

## Hard Boundaries

- Do not claim P6 is validated or sealed.
- Do not modify `alters/current/**` active YAML without explicit approval.
- Do not modify `alters/calibration/rubric.yaml` without explicit approval.
- Do not commit runtime records, personal weekly notes, secrets, logs, or provider outputs.
- Do not connect a real provider or make live provider calls without explicit configuration and confirmation.
- Do not add a database, hosted service, or deployment path unless the user approves a new scope.

## Verification Commands

```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q
cd apps/web && npm run build
python3 tools/build_deb.py
python3 tools/p8_provider_safety_audit.py --json
```

Run the relevant subset for documentation-only changes; run the full set before code or packaging commits.

## Documentation Maintenance Rule

Before every commit-sized change, update the handoff docs if status, tests, commands, boundaries, workflows, routes, pages, evidence, or next steps changed:

- `docs/harness/START_HERE_FOR_NEW_SESSION.md`
- `docs/harness/CURRENT_SESSION_CONTEXT.md`
- `docs/harness/PROJECT_BOARD.md`
- `docs/harness/TASK_QUEUE.md`
- `docs/harness/RUN_LOG.md`
- `docs/harness/EVIDENCE_INDEX.md`
- `README.md`
- `CLAUDE.md`
- this file

If no documentation update is needed, state why in the completion report. New sessions must be able to continue from the docs without reconstructing state from git log.
