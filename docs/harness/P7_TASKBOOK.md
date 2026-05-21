# P7 Taskbook

## One-Page Execution Summary

P7 turns Alters Lab from a repo-based developer app into an installable local Linux application. The release candidate must install under `/opt/alters-lab`, launch with `alters-lab` or a desktop launcher, serve the built frontend through FastAPI, store runtime records in user-owned directories, and preserve active YAML/rubric safety.

P7 exists to make P6 real-use validation possible without coding tools. It does not validate P6, seal P6, or fabricate P6 records.

Execution rules:

- No changes to `alters/current/**`.
- No changes to `alters/calibration/rubric.yaml`.
- No raw runtime records committed.
- Provider disabled/mock by default.
- Real provider explicit only.
- Frontend cannot call controlled persist or promotion live execution endpoints.
- Packaged mode writes to user data directories, not repo paths.
- Local server binds to `127.0.0.1` by default.

## Milestone Table

| ID | Title | Status | Depends On | PASS Criteria | BLOCKED Criteria |
|----|-------|--------|------------|---------------|------------------|
| P7-000 | Local App Distribution Boundary Plan | done | P6 code complete, P6 not validated | P7 docs created; governance updated; P6 remains not validated and not sealed | Any runtime code, frontend code, packaging script, active YAML, rubric, or raw runtime record changed |
| P7-M1 | Runtime Layout Externalization | done | P7-000 | Dev mode still uses repo-compatible paths; packaged mode writes runtime records under `~/.local/share/alters-lab`; active YAML/rubric protected | Runtime writes still hardcoded to repo paths; active YAML/rubric can be written by packaged runtime |
| P7-M2 | Unified Local Server | done | P7-M1 | FastAPI serves API and built frontend; `/local-app/health`, `/local-app/status`, and `/local-app/frontend-status` work; no Vite required in production | Separate frontend dev server required for packaged use |
| P7-M3 | CLI Launcher | done | P7-M2 | `alters-lab start/stop/status/open/doctor` works; logs written under runtime logs dir; port conflicts handled | App launch requires Codex, Claude Code, curl, pytest, or manual scripts |
| P7-M4 | Provider Configuration UI/API | done | P7-M3 | UI/API support disabled/mock/openai-compatible-http; secrets stored locally and redacted; key never returned | API response, log, or committed file exposes provider key |
| P7-M5 | Debian Package Build | done | P7-M4 | `.deb` installs app code to `/opt/alters-lab`, launcher to `/usr/bin/alters-lab`, and preserves user runtime data | Package writes or owns user runtime data |
| P7-M6 | Desktop Integration | done | P7-M5 | Desktop launcher starts local app and opens browser to local UI | Launcher depends on repo checkout or dev tooling |
| P7-M7 | Upgrade / Uninstall / Data Safety | done | P7-M6 | Upgrade preserves user data; uninstall preserves data unless explicit purge; backup/export command exists | Upgrade/uninstall deletes user config, data, logs, or secrets by default |
| P7-M8 | Local App Release Candidate | done | P7-M7 | Install deb, start app, open frontend, show provider status, run weekly review, store record in user data dir, P6 remains not sealed | Smoke test requires coding tools or mutates active YAML/rubric |
| P7-M9 | P7 Closeout | ready_with_approval | P7-M8 | Release candidate evidence complete; P8 remains blocked; P6 validation state unchanged unless real evidence later exists | P7 closeout claims P6 validation or starts P8 |

## Dependencies

- P7-M1 depends on this boundary plan and human approval.
- P7-M2 depends on runtime path externalization.
- P7-M3 depends on a unified backend serving UI and API.
- P7-M4 depends on the launcher/status surface so provider configuration can be exercised as a local app.
- P7-M5 depends on stable app start behavior and provider config boundaries.
- P7-M6 depends on package-owned launcher paths.
- P7-M7 depends on package/install behavior.
- P7-M8 depends on all local app pieces being integrated.
- P7-M9 depends on release candidate smoke evidence.

## Cross-Cutting PASS Criteria

- Active YAML and rubric remain unchanged.
- Provider output cannot write active YAML.
- Provider secrets are never committed, logged, or returned.
- Runtime records live under user data directories in packaged mode.
- Local server binds to `127.0.0.1` by default.
- P6 remains `CODE_COMPLETE`, `NOT_VALIDATED`, and `NOT_SEALED` unless a later real-use window provides verified evidence.

## Cross-Cutting BLOCKED Criteria

- Any P7 milestone attempts to seal P6.
- Any P7 milestone creates fake weekly review, calibration, pattern review, or behavior validation records.
- Any packaged runtime writes into repo runtime paths.
- Any frontend route calls controlled persist or promotion live execution endpoints.
- Any package lifecycle script deletes user data by default.
