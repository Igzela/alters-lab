# P7 Packaging Boundary

## Debian Package Contents

The `.deb` package installs app code and launch integration only.

Package-owned contents:

- FastAPI backend application code.
- Built React frontend static assets.
- Python runtime/dependency environment or packaged dependency bundle.
- CLI launcher.
- Desktop launcher.
- Optional icon.
- Package metadata and maintainer scripts required for installation.

The package must not contain:

- Provider API keys.
- `.env` files.
- User config.
- User secrets.
- Raw P6 runtime records.
- Generated weekly review records.
- Generated calibration records.
- Generated behavior validation records.
- User logs.

## Files Installed

Expected package-installed paths:

- `/opt/alters-lab/`
- `/usr/bin/alters-lab`
- `/usr/share/applications/alters-lab.desktop`
- Optional icon under a package-owned icon path such as `/usr/share/icons/hicolor/.../apps/alters-lab.png`.

Expected runtime-created user paths:

- `~/.config/alters-lab/config.yaml`
- `~/.config/alters-lab/secrets.yaml` only as chmod `0600` fallback.
- `~/.local/share/alters-lab/`
- `~/.local/state/alters-lab/logs/`

## Files Not Installed

The `.deb` must not install or overwrite:

- `~/.config/alters-lab/config.yaml`
- `~/.config/alters-lab/secrets.yaml`
- `~/.local/share/alters-lab/**`
- `~/.local/state/alters-lab/**`
- Any user home directory runtime record.
- `alters/current/**` as writable runtime state.
- `alters/calibration/rubric.yaml` as writable runtime state.

Default config templates may ship under `/opt/alters-lab`, but user config creation must be idempotent and preserve existing user files.

## User Data Preservation

Upgrade policy:

- Preserve `~/.config/alters-lab`.
- Preserve `~/.local/share/alters-lab`.
- Preserve `~/.local/state/alters-lab`.
- Never delete provider secrets.
- Never rewrite existing runtime records without explicit user action.

Uninstall policy:

- Remove package-owned files.
- Preserve user config, secrets, data, and logs.
- Do not delete user data unless a separately approved explicit purge command exists.

Purge policy:

- Not implemented in P7-000.
- Must require explicit future approval before any destructive data deletion behavior is added.

## Desktop Integration

Desktop launcher target:

- Runs `alters-lab open` or equivalent launcher behavior.
- Starts the local backend when needed.
- Opens the local browser target at `http://127.0.0.1:18790/`.

Launcher requirements:

- Must not require Codex or Claude Code.
- Must not require a repo checkout.
- Must write logs under `~/.local/state/alters-lab/logs`.
- Must report port conflicts through `alters-lab status` or `alters-lab doctor`.

## Package Smoke Test Checklist

- Install with `sudo apt install ./alters-lab.deb`.
- Confirm `/opt/alters-lab` exists.
- Confirm `/usr/bin/alters-lab` exists and is executable.
- Confirm desktop file exists under `/usr/share/applications`.
- Run `alters-lab doctor`.
- Run `alters-lab start`.
- Run `alters-lab status`.
- Open frontend through the unified local server.
- Confirm `/local-app/health` responds.
- Confirm `/local-app/status` responds.
- Confirm provider status is visible and secrets are redacted.
- Run weekly review flow from user-provided real input.
- Confirm runtime record is stored under `~/.local/share/alters-lab/product/weekly_reviews/`.
- Confirm logs are stored under `~/.local/state/alters-lab/logs/`.
- Confirm `alters/current/**` is unchanged.
- Confirm `alters/calibration/rubric.yaml` is unchanged.
- Confirm P6 behavior validation remains not sealed unless real evidence later satisfies the P6 gate.

