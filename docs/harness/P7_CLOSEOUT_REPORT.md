# P7 Closeout Report

## Status

P7 closeout status: **PASS**

Phase 7 is sealed as a local Linux app release candidate. This seals local app distribution readiness only. It does not validate P6 behavior, does not seal P6, and does not start P8.

P6 remains: **CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED**.

P8 remains: **blocked**.

## Milestone Table

| Milestone | Status | Result |
|-----------|--------|--------|
| P7-000 | done | Local app distribution boundary planned |
| P7-M1 | done | Runtime layout externalized |
| P7-M2 | done | Unified local server added |
| P7-M3 | done | CLI launcher added |
| P7-M4 | done | Provider configuration UI/API added |
| P7-M5 | done | Debian package build added |
| P7-M6 | done | Desktop integration added |
| P7-M7 | done | Upgrade/uninstall/data safety added |
| P7-M8 | done | Package-context release-candidate smoke passed |
| P7-M9 | done | Closeout completed |

## Local App Capabilities

- Installs app code under `/opt/alters-lab`.
- Launches through `alters-lab` CLI.
- Supports `start`, `stop`, `status`, `open`, `doctor`, and `backup`.
- Serves the built React frontend from FastAPI.
- Binds local server to `127.0.0.1` by default.
- Resolves packaged runtime config under `~/.config/alters-lab/config.yaml`.
- Resolves packaged runtime data under `~/.local/share/alters-lab/product`.
- Resolves logs under `~/.local/state/alters-lab/logs`.
- Supports desktop launcher through `/usr/share/applications/alters-lab.desktop`.

## Package Build Summary

`tools/build_deb.py` builds `dist/deb/alters-lab_0.1.0_amd64.deb`.

The package includes:

- `/opt/alters-lab/apps/api`
- `/opt/alters-lab/web/dist`
- `/opt/alters-lab/.venv`
- `/usr/bin/alters-lab`
- `/usr/share/applications/alters-lab.desktop`
- `/usr/share/icons/hicolor/scalable/apps/alters-lab.svg`

The package excludes user-owned runtime state, secrets, logs, `.env` files, `node_modules`, and raw P6 runtime records.

## Package-Context Smoke Summary

P7-M8 smoke passed using `dpkg-deb -x` and an isolated `HOME`.

Verified:

- Packaged launcher status/doctor/start/stop.
- FastAPI `/local-app/health` and `/local-app/status`.
- Built frontend index and JS asset served by backend.
- Provider status/config/test redacted and mock-safe.
- Synthetic weekly note, weekly review, and action-alignment records wrote under isolated user data dirs.
- Backup dry-run planned data/config only and excluded secrets/logs by default.
- Server stopped after smoke.

The synthetic smoke records were temporary and are not P6 real-use evidence.

## Provider Config Safety

- Default provider mode remains disabled.
- Mock mode works without network calls.
- Real provider mode requires explicit configuration.
- API responses do not return provider keys.
- Provider output cannot write active YAML.
- Provider output cannot generate reality scores.
- Provider output does not persist by default.

## Data Safety And Backup

- Upgrade/uninstall policy preserves `~/.config/alters-lab`, `~/.local/share/alters-lab`, `~/.local/state/alters-lab`, and provider secrets.
- `alters-lab backup` excludes secrets by default.
- Logs require explicit inclusion.
- Secrets require exact confirmation before inclusion.
- Package maintainer scripts do not start services or delete user data.

## Desktop Integration

- Desktop file is package-owned.
- Desktop entry launches `alters-lab open`.
- Icon is installed through hicolor scalable app icon path.
- Desktop file contains no repo paths, user home paths, shell expansion, or secrets.

## Verification

| Check | Result |
|-------|--------|
| Backend tests | PASS, 949 passed |
| Frontend install/build | PASS |
| Debian package build | PASS |
| Package safety inspection | PASS |
| Package-context smoke | PASS |
| Active YAML diff | empty |
| Rubric diff | empty |
| Raw product runtime status | empty |
| Generated package/frontend artifacts | ignored |
| Secret scan | no real secrets; only code patterns, env-name references, dummy tests/templates |

## Boundaries Preserved

- No `alters/current/**` changes.
- No `alters/calibration/rubric.yaml` changes.
- No raw P6 runtime records committed.
- No provider secrets committed.
- No live provider calls added.
- No P6 behavior validation claim.
- No P6 seal claim.
- P8 not started.

## Known Limitations

- P6 behavior validation still requires real 4-week use.
- Actual `sudo apt install`, upgrade, remove, and purge smoke was skipped because no safe disposable system environment was used.
- P7 targets Linux/Debian local app distribution only, not cloud, SaaS, multi-user, mobile, Windows, or macOS.
- Real provider live calls are not enabled by default and were not tested with real keys.

## Final State

P7 is sealed as **LOCAL_APP_RELEASE_CANDIDATE**.

Recommended next action: begin real P6 validation using the local app, or start P8-000 only after explicit human/GPT approval.
