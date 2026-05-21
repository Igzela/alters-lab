# Debian Packaging

P7-M5 packaging installs application code and launcher integration only.

Package-owned paths:

- `/opt/alters-lab/apps/api`
- `/opt/alters-lab/web/dist`
- `/opt/alters-lab/.venv`
- `/usr/bin/alters-lab`
- `/usr/share/applications/alters-lab.desktop`
- `/usr/share/icons/hicolor/scalable/apps/alters-lab.svg`

User-owned paths are not packaged or deleted:

- `~/.config/alters-lab`
- `~/.local/share/alters-lab`
- `~/.local/state/alters-lab`

Maintainer scripts do not start services, write secrets, create root-owned user config, or delete user home data.

The desktop file launches the existing CLI with `alters-lab open`; it does not contain repo paths or user-home paths.

Upgrade/remove/purge policy:

- Preserve `~/.config/alters-lab`.
- Preserve `~/.local/share/alters-lab`.
- Preserve `~/.local/state/alters-lab`.
- Preserve provider secrets.
- Do not create root-owned user config.
- Do not start services from package scripts.
