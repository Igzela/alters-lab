# Install Alters Lab

## System Requirements

- Linux (Debian/Ubuntu or compatible)
- Python 3.10+
- `python3` available on PATH

## Install from .deb Package

If you have a pre-built package:

```bash
sudo apt install ./alters-lab_0.1.0_amd64.deb
```

Or with dpkg directly:

```bash
sudo dpkg -i alters-lab_0.1.0_amd64.deb
sudo apt -f install
```

## Build and Install from Source

```bash
# Clone the repository
git clone https://github.com/Igzela/alters-lab.git
cd alters-lab

# Build the .deb package
python3 tools/build_deb.py

# Install
sudo apt install ./dist/deb/alters-lab_0.1.0_amd64.deb
```

The build script stages the backend, frontend, and a bundled Python virtual environment into the package. No separate `npm install` or `pip install` is needed after installation.

## What Gets Installed

| Location | Contents |
|----------|----------|
| `/opt/alters-lab/` | Application code, bundled venv, frontend assets |
| `/usr/bin/alters-lab` | CLI launcher |
| `/usr/share/applications/alters-lab.desktop` | Desktop launcher |
| `/usr/share/icons/hicolor/scalable/apps/alters-lab.svg` | App icon |

## Where Your Data Lives

User data is stored under your home directory and is **not** removed on uninstall:

| Purpose | Path |
|---------|------|
| Config | `~/.config/alters-lab/config.yaml` |
| Secrets | `~/.config/alters-lab/secrets.yaml` (chmod 0600) |
| Data | `~/.local/share/alters-lab/product/` |
| Logs | `~/.local/state/alters-lab/logs/` |

## Verify Installation

```bash
# Check CLI is available
alters-lab doctor

# Start the app
alters-lab start

# Check status
alters-lab status
```

The app runs at `http://127.0.0.1:18790` by default.

## Next Steps

See the [First-Run Checklist](FIRST_RUN_CHECKLIST.md) for what to do after installation.

If anything goes wrong, see [Troubleshooting](TROUBLESHOOTING.md).
