# Alters Lab — User Guide

Alters Lab is a personal tool for exploring potential future life paths. It captures your current state, discovers structural branching decisions, generates alter versions of yourself for each path, facilitates dialogue between you and those alters, and calibrates which branches best match your values.

## Quick Start

### 1. Install the .deb Package

Download and install the Debian package:

```bash
sudo apt install ./alters-lab_0.1.0_amd64.deb
```

Or build from source:

```bash
python tools/build_deb.py
sudo dpkg -i dist/deb/alters-lab_0.1.0_amd64.deb
```

### 2. Launch the App

```bash
# Start the app (opens browser automatically)
alters-lab start

# Or just open (starts server if not running)
alters-lab open

# Check status
alters-lab status

# Health check
alters-lab doctor
```

The app runs at `http://127.0.0.1:18790` by default.

### 3. Configure a Provider (Optional)

If you want real LLM-powered dialogue and weekly reviews, configure an OpenAI-compatible provider. See [Provider Configuration](PROVIDER_CONFIGURATION.md) for details.

Quick setup via API:

```bash
# Set provider mode and endpoint
curl -X POST http://127.0.0.1:18790/provider-config/config \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "openai-compatible-http",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o",
    "timeout_seconds": 60,
    "secret_storage": "keyring",
    "key_name": "alters-lab/provider-api-key",
    "explicit_user_configuration": true
  }'

# Store your API key
curl -X POST http://127.0.0.1:18790/provider-config/secret \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your-api-key",
    "storage": "keyring",
    "confirmation": "store-secret"
  }'
```

## Workflow Walkthrough

The Alters Lab workflow follows a core loop:

```
Snapshot → Branches → Alters → Dialogue → Calibration
```

### 1. Snapshot Intake

Capture your current life state — the starting point for all branch generation.

- **Heaviest constraint**: What is the binding constraint in your life right now?
- **Most unclear**: What direction is most uncertain?
- **Unwilling to give up**: What is non-negotiable?

The snapshot is stored in `alters/current/snapshot.yaml`.

### 2. Branch Discovery

From your snapshot, the system identifies 3–4 structural, mutually incompatible future branches. Each branch represents a fundamentally different direction — not a small variation, but a distinct path.

Branches are stored in `alters/current/branches.yaml`.

### 3. Alter Generation

For each branch, an Alter is generated — a coherent version of you living that path. Each Alter includes:

- A life state projection (location, daily structure, social context)
- Tradeoffs (what is gained vs. lost)
- Personality drift estimates against the rubric
- A narrative grounding the Alter in real snapshot anchors

Alters are stored in `alters/current/alters/`.

### 4. Dialogue

Converse with each Alter to evaluate fit, values, and tradeoffs. If a provider is configured, dialogues use real LLM responses. Without a provider, mock responses are used.

Dialogue records are stored in the product state directory.

### 5. Calibration

Score branches against a personal rubric (4-axis: execution discipline, exploration freedom, identity stability, risk tolerance). Compare predicted values against actual outcomes over time.

The rubric is stored in `alters/calibration/rubric.yaml`.

## Provider Setup

Alters Lab works without any LLM provider. Provider features (alter dialogue, weekly reviews) use mock responses by default.

To enable real LLM responses, configure an OpenAI-compatible HTTP provider. See [Provider Configuration](PROVIDER_CONFIGURATION.md) for the complete guide.

Supported providers include:
- OpenAI (GPT-4o, GPT-4, etc.)
- MiMo API
- Any local server exposing an OpenAI-compatible `/chat/completions` endpoint

## Backup and Data Safety

### Backup

```bash
# Preview what would be backed up
alters-lab backup --dry-run --json

# Create a backup
alters-lab backup --output ~/alters-lab-backup.tar.gz

# Include logs
alters-lab backup --include-logs

# Include secrets (requires confirmation)
alters-lab backup --include-secrets --confirm-include-secrets include-secrets-in-backup
```

**Default backup includes:**
- `~/.local/share/alters-lab` (product data)
- `~/.config/alters-lab/config.yaml` (config)

**Default backup excludes:**
- `~/.config/alters-lab/secrets.yaml` (API keys)
- Logs

### Data Locations

| Data | Location |
|------|----------|
| App code | `/opt/alters-lab` (packaged) or repo root (dev) |
| Config | `~/.config/alters-lab/config.yaml` |
| Secrets | `~/.config/alters-lab/secrets.yaml` (fallback) or system keyring |
| Product data | `~/.local/share/alters-lab/product/` |
| Logs | `~/.local/state/alters-lab/logs/` |

### Upgrade and Uninstall

- **Upgrade**: Preserves all user-owned data (`~/.config/alters-lab`, `~/.local/share/alters-lab`, `~/.local/state/alters-lab`).
- **Uninstall**: Deletes package-owned files (`/opt/alters-lab`, `/usr/bin/alters-lab`). User data is preserved.
- **Purge**: Not implemented. User data is never deleted by package scripts.

## CLI Commands

| Command | Description |
|---------|-------------|
| `alters-lab start` | Start the local server (background by default) |
| `alters-lab start --foreground` | Start in foreground mode |
| `alters-lab stop` | Stop the local server |
| `alters-lab status` | Show server status |
| `alters-lab doctor` | Run health checks |
| `alters-lab open` | Open the app in a browser (starts server if needed) |
| `alters-lab backup` | Create a data backup |

### Common Options

- `--mode dev|packaged` — Override runtime mode
- `--host HOST` — Override server host (default: `127.0.0.1`)
- `--port PORT` — Override server port (default: `18790`)
- `--json` — Output as JSON

## Desktop Integration

When installed via `.deb`, Alters Lab integrates with your desktop environment:

- Application launcher entry in your app menu
- Desktop icon via hicolor scalable app icon
- Launch via `alters-lab open` or the desktop entry
