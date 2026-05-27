# Data and Backup

## Where Your Data Lives

| Purpose | Path | Description |
|---------|------|-------------|
| Config | `~/.config/alters-lab/config.yaml` | Provider mode, base URL, model settings |
| Secrets | `~/.config/alters-lab/secrets.yaml` | API keys (chmod 0600, never committed) |
| Data | `~/.local/share/alters-lab/product/` | Weekly reviews, calibration records, workflow runs |
| Logs | `~/.local/state/alters-lab/logs/` | Server logs |

## Backup

Create a backup of your data and config:

```bash
alters-lab backup
```

This creates a `.tar.gz` archive under `~/.local/share/alters-lab/product/exports/`.

### What's Included by Default

- All product data (weekly reviews, calibration records, workflow runs)
- Config file (`config.yaml`)

### What's Excluded by Default

- **Logs** — large and rarely needed. Add with `--include-logs`.
- **Secrets** — API keys are sensitive. Add with `--include-secrets --confirm-include-secrets include-secrets-in-backup`.

### Backup Options

```bash
# Dry run — see what would be included without creating the archive
alters-lab backup --dry-run --json

# Custom output path
alters-lab backup --output /path/to/backup.tar.gz

# Include logs
alters-lab backup --include-logs

# Include secrets (requires explicit confirmation)
alters-lab backup --include-secrets --confirm-include-secrets include-secrets-in-backup

# Exclude config
alters-lab backup --no-include-config
```

## Restore

To restore from a backup:

```bash
# Extract to home directory
tar xzf alters-lab_backup_*.tar.gz -C ~
```

After restoring, restart the app:

```bash
alters-lab start
```

## Data Safety

- Secrets are stored with `chmod 0600` — only your user can read them.
- The backup archive excludes secrets by default.
- API keys are never returned by API responses or written to logs.
- The `.deb` package does not touch user data directories during install, upgrade, or uninstall.

## P6 Runtime Records

If you use the Weekly Review feature, runtime records are written under `~/.local/share/alters-lab/product/`. These records are personal evidence for calibration and are not committed to the repository.
