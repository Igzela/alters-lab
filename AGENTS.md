# Agent Instructions

This repository is Alters Lab, a local personal future-path simulation and calibration tool.

## New Session Bootstrap

Every Codex, Claude Code, or other coding-agent session must start by reading:

1. `CLAUDE.md` — project state, tech stack, doc maintenance rules, **待办任务**
2. `AGENTS.md` (this file) — collaboration protocol, hard boundaries, verification commands
3. `docs/architecture.md` — how the system works
4. `docs/data-model.md` — schema definitions

**DO NOT read `docs/harness/`** — it has been deleted. Historical milestone docs no longer exist.

## Current State

- P0-P14 are complete. Project is open-source (MIT LICENSE).
- P6 remains `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`.
- Product is usable as a local personal tool. Sample data ships at `alters/sample/` (load via `alters-lab load-sample`).
- Docker support: `docker compose up -d` starts the app at http://localhost:18790.
- Technical hardening done: structured logging, CORS middleware, rate limiting (600 req/min), dependency pinning.
- 1980 backend tests passing, 90 frontend tests passing, frontend build clean.

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
- Code > `docs/data-model.md` > `docs/architecture.md` > `CLAUDE.md` > `README.md`

## Commit前强制检查清单

**Every commit must pass this checklist BEFORE `git add`. Missing even one item is a BLOCKED review.**

```
□ 1. README.md     — 用户可见功能变了？（新页面、新功能、测试数变化）
□ 2. CLAUDE.md     — 测试数变了？待办任务变了？系统状态变了？
□ 3. AGENTS.md     — 协作方式或硬边界变了？
□ 4. architecture.md — 新增/修改了 API router、service、中间件？
□ 5. data-model.md — 新增/修改了 Pydantic schema？
□ 6. product-spec.md — 新增/修改了产品功能？
□ 7. 运行测试确认 — 测试数与 CLAUDE.md 一致？
```

**执行方式：** 逐条回答"是/否"。回答"是"的条目必须更新对应文档。回答"否"的跳过。不能因为"文档看起来差不多"就跳过检查。

**常见失败：**
- 新增了 API router 但没更新 architecture.md
- 新增了 schema 但没更新 data-model.md
- 测试数变了但没更新 CLAUDE.md
- 新增了产品功能但没更新 README.md
