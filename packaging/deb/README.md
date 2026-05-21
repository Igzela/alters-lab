# Debian Packaging

P7-M5 packaging installs application code and launcher integration only.

Package-owned paths:

- `/opt/alters-lab/apps/api`
- `/opt/alters-lab/web/dist`
- `/opt/alters-lab/.venv`
- `/usr/bin/alters-lab`

User-owned paths are not packaged or deleted:

- `~/.config/alters-lab`
- `~/.local/share/alters-lab`
- `~/.local/state/alters-lab`

Maintainer scripts do not start services, write secrets, create root-owned user config, or delete user home data.
