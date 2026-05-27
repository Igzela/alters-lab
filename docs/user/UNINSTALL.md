# Uninstall Alters Lab

## Stop the Server

Before uninstalling, stop the running server:

```bash
alters-lab stop
```

## Remove the Package

```bash
sudo apt remove alters-lab
```

Or with dpkg:

```bash
sudo dpkg -r alters-lab
```

## What Gets Removed

- `/opt/alters-lab/` — application code, bundled venv, frontend assets
- `/usr/bin/alters-lab` — CLI launcher
- `/usr/share/applications/alters-lab.desktop` — desktop launcher
- `/usr/share/icons/hicolor/scalable/apps/alters-lab.svg` — app icon

## What Gets Preserved

User data is **not** removed by `apt remove`. These directories remain:

| Path | Contents |
|------|----------|
| `~/.config/alters-lab/` | Config and secrets |
| `~/.local/share/alters-lab/` | Product data, weekly reviews, calibration records |
| `~/.local/state/alters-lab/` | Logs |

This is intentional — your data survives uninstall so you don't lose calibration history or provider configuration.

## Full Cleanup

If you want to remove all user data after uninstalling:

```bash
# Back up first (optional)
tar czf alters-lab-backup.tar.gz \
  ~/.config/alters-lab \
  ~/.local/share/alters-lab \
  ~/.local/state/alters-lab

# Remove user data
rm -rf ~/.config/alters-lab
rm -rf ~/.local/share/alters-lab
rm -rf ~/.local/state/alters-lab
```

## Reinstall

To reinstall after uninstalling:

```bash
sudo apt install ./alters-lab_0.1.0_amd64.deb
```

Your preserved data directories will be picked up automatically. Config, secrets, weekly reviews, and calibration records are intact.

## Upgrade

To upgrade to a newer version:

```bash
sudo apt install ./alters-lab_<new-version>_amd64.deb
```

User data is preserved on upgrade. No special steps needed.
