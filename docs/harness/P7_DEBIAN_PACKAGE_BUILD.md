# P7 Debian Package Build

P7-M5 adds a reproducible Debian package build path for the local app release candidate.

## Build Command

```bash
python tools/build_deb.py
```

The script builds the React frontend, stages package files under `build/deb/alters-lab`, creates a Python virtual environment under `/opt/alters-lab/.venv` inside the package, installs the backend package into that venv, and writes the package to `dist/deb/alters-lab_0.1.0_amd64.deb`.

## Package Contents

Installed package-owned paths:

- `/opt/alters-lab/apps/api/src`
- `/opt/alters-lab/apps/api/pyproject.toml`
- `/opt/alters-lab/web/dist`
- `/opt/alters-lab/.venv`
- `/usr/bin/alters-lab`

The launcher sets:

- `ALTERS_LAB_MODE=packaged` unless already set.
- `PYTHONPATH=/opt/alters-lab/apps/api/src`.

It then executes:

```bash
/opt/alters-lab/.venv/bin/python -m alters_lab.cli "$@"
```

with a fallback to `python3 -m alters_lab.cli` if the bundled venv is unavailable.

## Exclusions

The package build excludes:

- `node_modules`
- `.env` and `.env.local`
- `alters/product` runtime records
- user config, data, logs, and secrets paths
- `.deb` artifacts from git

## Data Safety

The `.deb` package installs app code only. User config, secrets, data, and logs stay under user-owned home directories and are preserved on upgrade/remove. Maintainer scripts only print messages; they do not create root-owned user config, start services, write secrets, or delete user data.

## P6 Boundary

P7-M5 does not validate P6, seal P6, or fabricate weekly review, calibration, pattern review, or behavior validation records. P6 remains `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`.
