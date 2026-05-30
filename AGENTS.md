# Agent Instructions

This repository is Alters Lab, a local personal future-path simulation and calibration tool.

## New Session Bootstrap

Every Codex, Claude Code, or other coding-agent session must start by reading:

1. `CLAUDE.md` — project state, tech stack, doc maintenance rules, **待办任务**
2. `AGENTS.md` (this file) — collaboration protocol, hard boundaries, verification commands
3. `docs/architecture.md` — how the system works
4. `docs/data-model.md` — schema definitions

**DO NOT read `docs/harness/`** — it contains stale milestone governance docs (P0-P14). They are historical records, not current state. Always trust CLAUDE.md over harness docs.

## Current State

- P0-P14 are complete. Project is open-source (MIT LICENSE).
- P6 remains `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`.
- Product is usable as a local personal tool. Sample data ships at `alters/sample/` (load via `alters-lab load-sample`).
- Technical hardening done: structured logging, CORS middleware, rate limiting (600 req/min), dependency pinning.
- 1269 backend tests passing, frontend build clean.

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
```

Run the relevant subset for documentation-only changes; run the full set before code or packaging commits.

## Documentation Maintenance Rule

Before every commit-sized change, check which docs are affected (see `CLAUDE.md` § 文档维护规范). Update only what changed — don't rubber-stamp all files.

Priority order for conflict resolution:
- Code > `docs/data-model.md` > `docs/architecture.md` > `CLAUDE.md` > `README.md` > `docs/harness/`
