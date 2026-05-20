# P7-000 Local App Distribution Boundary Plan

## 1. Current State

Phase 6 runtime code is complete and merged to `main`, but Phase 6 behavior validation is not complete. P6 is not sealed.

P6 remains blocked by the real-use validation window. The system still requires verified persisted evidence from real use before it can return `P6_BEHAVIOR_VALIDATED` or pass Phase 6 closeout.

P7 starts because real use should not depend on Codex, Claude Code, curl, pytest, or manual scripts. P7 may make the system usable as an independent local app, but it must not turn setup progress into behavior-validation evidence.

## 2. Product Goal

P7 creates an installable local Linux application release candidate for Alters Lab.

The target user experience is:

- Install with `sudo apt install ./alters-lab.deb`.
- Launch with `alters-lab` or a desktop launcher.
- Use a local application with backend, frontend, provider configuration, runtime records, logs, and data safety boundaries.
- Continue P6 real-use validation without coding tools.

The product target includes:

- FastAPI backend.
- Built React frontend served by the backend in production.
- Local provider configuration with secret redaction.
- User-owned runtime data directory.
- Desktop launcher.
- Debian package.

## 3. Non-Goals

P7 is not:

- SaaS.
- Cloud deployment.
- Multi-user accounts.
- Production auth.
- Windows or macOS packaging.
- Automatic semantic mutation.
- A P6 validation shortcut.
- A public hosted product.
- Mobile app work.
- A reason to start P8.

## 4. Runtime Layout

Application code:

- `/opt/alters-lab`

User config:

- `~/.config/alters-lab/config.yaml`

User secrets:

- Preferred: system keyring when available.
- Fallback: `~/.config/alters-lab/secrets.yaml` with mode `0600`.

User data:

- `~/.local/share/alters-lab`

Runtime records:

- `~/.local/share/alters-lab/product/weekly_notes/`
- `~/.local/share/alters-lab/product/weekly_reviews/`
- `~/.local/share/alters-lab/product/calibration_records/`
- `~/.local/share/alters-lab/product/pattern_reviews/`
- `~/.local/share/alters-lab/product/behavior_validation/`
- `~/.local/share/alters-lab/product/exports/`

Logs:

- `~/.local/state/alters-lab/logs/`

## 5. Dev Mode vs Packaged Mode

Dev mode may use repo paths so existing tests, local commands, and implementation workflows remain compatible.

Packaged mode must use user data directories. Production runtime writes must not depend on the repository being present or writable.

Both modes must keep these files protected:

- `alters/current/**`
- `alters/calibration/rubric.yaml`

No P7 code may make provider output, frontend actions, or packaged runtime startup write active YAML or the rubric.

## 6. Provider Policy

Provider mode defaults to mock or disabled.

Real provider use must be explicit. A configured provider may be `openai-compatible-http`, but no real key can be committed, returned by API responses, or written to logs.

Provider policy:

- API keys are never returned by API responses.
- Config/status APIs redact secret fields.
- Provider output is not persistent by default.
- Provider output never writes active YAML.
- Provider output never auto-generates a reality score.
- Weekly review facts must remain grounded in user-provided evidence.

## 7. Frontend Policy

In production, the built frontend is served by the FastAPI backend. Users should not need a Vite dev server for packaged use.

The frontend must not call dangerous endpoints, including controlled persist endpoints, promotion live execution endpoints, or any endpoint that can mutate active YAML.

The frontend should expose:

- Weekly review flow.
- Provider status and configuration state.
- Calibration history.
- Local app status and health.
- Data/export affordances that operate only on user runtime data.

## 8. Packaging Policy

The `.deb` package installs app code only.

Package-owned paths:

- `/opt/alters-lab`
- `/usr/bin/alters-lab`
- `/usr/share/applications/alters-lab.desktop`
- Optional icon path under package-owned system directories.

User-owned paths:

- `~/.config/alters-lab`
- `~/.local/share/alters-lab`
- `~/.local/state/alters-lab`

Upgrade preserves user data and config.

Uninstall preserves user data and config unless an explicit purge path is later designed and approved.

## 9. P6 Interaction

P7 enables real P6 use by making the application installable and launchable without coding tools.

P7 does not validate P6.

P7 does not seal P6.

P7 must not fabricate P6 weekly review records, calibration records, pattern reviews, or behavior validation results.

P6 validation resumes once the local app is usable and Charlie has real weekly evidence.

## 10. P7 Milestones

| ID | Title | Target Status | Scope |
|----|-------|---------------|-------|
| P7-000 | Local App Distribution Boundary Plan | done | Planning docs, governance updates, data-safety policy |
| P7-M1 | Runtime Layout Externalization | ready_with_approval | Refactor production runtime writes to user data dirs while preserving dev mode |
| P7-M2 | Unified Local Server | blocked | Serve built frontend from FastAPI with local-app health/status |
| P7-M3 | CLI Launcher | blocked | Add `alters-lab` start/stop/status/open/doctor commands |
| P7-M4 | Provider Configuration UI/API | blocked | Local provider settings, secret storage, redacted status |
| P7-M5 | Debian Package Build | blocked | Build `.deb` installing code and launcher only |
| P7-M6 | Desktop Integration | blocked | Desktop launcher and optional icon |
| P7-M7 | Upgrade / Uninstall / Data Safety | blocked | Preserve user data and add backup/export behavior |
| P7-M8 | Local App Release Candidate | blocked | Install/start/open/provider/weekly-review smoke test |
| P7-M9 | P7 Closeout | blocked | Verify release candidate and keep P8 blocked |

