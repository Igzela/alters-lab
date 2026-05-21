# P7 Data Safety

P7-M7 hardens upgrade, uninstall, and backup boundaries before local app release candidate testing.

## Upgrade Policy

Package upgrades preserve user-owned paths:

- `~/.config/alters-lab`
- `~/.local/share/alters-lab`
- `~/.local/state/alters-lab`

The Debian package owns app files under `/opt/alters-lab`, `/usr/bin/alters-lab`, `/usr/share/applications/alters-lab.desktop`, and the hicolor app icon. It does not own user home data.

## Uninstall Policy

Package removal deletes package-owned files through dpkg behavior. Maintainer scripts do not delete user config, data, logs, or provider secrets.

Preserved on remove:

- local config
- fallback secrets file
- runtime product records
- exports
- logs

## Purge Policy

P7-M7 does not implement destructive purge behavior. Even purge scripts must preserve user home data unless a future explicit purge command is separately approved.

## Backup Policy

Command:

```bash
alters-lab backup --dry-run --json
alters-lab backup --output ~/alters-lab-backup.tar.gz
```

Default backup includes:

- `~/.local/share/alters-lab`
- `~/.config/alters-lab/config.yaml` when present

Default backup excludes:

- `~/.config/alters-lab/secrets.yaml`
- provider API keys
- logs

Logs can be included with:

```bash
alters-lab backup --include-logs
```

Secrets are excluded by default because backup archives are easy to move, inspect, upload, or commit accidentally. Secret inclusion requires explicit confirmation:

```bash
alters-lab backup --include-secrets --confirm-include-secrets include-secrets-in-backup
```

This is intended only for deliberate local archival. It should not be used for routine evidence sharing.

## P6 Boundary

Backup/export does not validate P6, seal P6, fabricate weekly review records, or modify active YAML/rubric. P6 remains `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`.
