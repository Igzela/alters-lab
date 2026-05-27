# Alters System Lab

A personal future-branch simulation and calibration system.

## Overview

Alters System helps you explore potential future paths by modelling branching life decisions, generating alter versions of yourself for each path, and calibrating which branches best align with your values and energy.

## Quick Start

### 1. Install

Download and install the Debian package:

```bash
sudo apt install ./alters-lab_0.1.0_amd64.deb
```

Or build from source:

```bash
python tools/build_deb.py
sudo dpkg -i dist/deb/alters-lab_0.1.0_amd64.deb
```

### 2. Launch

```bash
# Start the app (opens browser automatically)
alters-lab start

# Or just open (starts server if not running)
alters-lab open
```

The app runs at `http://127.0.0.1:18790`.

### 3. Configure a Provider (Optional)

Alters Lab works without any LLM provider (uses mock responses). To enable real LLM-powered dialogue and weekly reviews, configure an OpenAI-compatible provider:

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

See [Provider Setup](docs/user/PROVIDER_SETUP.md) for the full guide.

## Provider Configuration

Alters Lab supports three provider modes:

| Mode | Description |
|------|-------------|
| `disabled` | No LLM calls. Default out of the box. |
| `mock` | Simulated responses. For testing without an API key. |
| `openai-compatible-http` | Real LLM calls to any OpenAI-compatible API. |

Configure via API endpoints or environment variables:

| Variable | Description |
|----------|-------------|
| `ALTERS_PROVIDER_MODE` | Provider mode |
| `ALTERS_PROVIDER_BASE_URL` | API base URL (e.g. `https://api.openai.com/v1`) |
| `ALTERS_PROVIDER_API_KEY` | API key |
| `ALTERS_PROVIDER_MODEL` | Model name |

Config file: `~/.config/alters-lab/config.yaml`

See [Provider Configuration](docs/PROVIDER_CONFIGURATION.md) for details.

## Core Loop

```
Snapshot → Branches → Alters → Dialogue → Calibration
```

1. **Snapshot Intake** — Capture a current state: constraints, uncertainties, and what you refuse to give up
2. **Branch Discovery** — Identify 3–4 structural, mutually incompatible future branches
3. **Alter Generation** — For each branch, generate an Alter: a coherent version of you living that path
4. **Dialogue / Value Alignment** — Converse with each Alter to evaluate fit, values, and tradeoffs
5. **Calibration** — Score branches against a Rubric and refine over time

## Project Status

All 8 phases complete:

| Phase | Status | Description |
|-------|--------|-------------|
| P0 | ✅ Done | File-based workflow (YAML snapshots, branches, alters) |
| P1 | ✅ Done | Data model and schema validation |
| P2 | ✅ Done | Snapshot intake and branch discovery |
| P3 | ✅ Done | Alter generation and draft review |
| P4 | ✅ Done | Calibration loop MVP |
| P5 | ✅ Done | Productization and provider gateway |
| P6 | ✅ Code-complete | Personal long-term use hardening (validation skipped by decision) |
| P7 | ✅ Done | Local app distribution (.deb, CLI, desktop integration) |
| P8 | ✅ Done | Real provider integration and end-to-end validation |

## CLI Commands

| Command | Description |
|---------|-------------|
| `alters-lab start` | Start the local server |
| `alters-lab stop` | Stop the local server |
| `alters-lab status` | Show server status |
| `alters-lab doctor` | Run health checks |
| `alters-lab open` | Open the app in a browser |
| `alters-lab backup` | Create a data backup |

## Documentation

- [First-Run Checklist](docs/user/FIRST_RUN_CHECKLIST.md) — What to do after installation
- [User Guide](docs/USER_GUIDE.md) — Quick start, workflow walkthrough, and reference
- [Provider Setup](docs/user/PROVIDER_SETUP.md) — How to configure LLM providers
- [Provider Safety](docs/user/PROVIDER_SAFETY.md) — Secret handling, output safety, confirmation gating
- [Troubleshooting](docs/user/TROUBLESHOOTING.md) — Common issues and how to fix them
- [Product Specification](docs/product-spec.md) — System design and concepts
- [Alter Generation Workflow](docs/alter-generation-workflow.md) — How alters are generated
- [Branch Discovery Workflow](docs/branch-discovery-workflow.md) — How branches are discovered
- [Calibration System Workflow](docs/calibration-system-workflow.md) — How calibration works

## Project Structure

```
alters/
  current/
    snapshot.yaml          # Current state: constraints, uncertainties, anchors
    branches.yaml          # Discovered branches with quality rules
    reality_trace.yaml     # How reality diverges from branches over time
    alters/                # Alter YAML files per branch
  calibration/
    rubric.yaml            # Evaluation dimensions (4-axis rubric)
    state.json             # Cold-start calibration state
    scores/                # Per-cycle score records
  archive/                 # Completed cycle archives
```

## Browser Automation (chrome-devtools MCP)

ChatGPT interaction uses the `chrome-devtools` MCP server (autoConnect mode).
It connects to the running Chrome instance — no separate scripts or CLI tools needed.

**Available MCP tools:** `list_pages`, `select_page`, `navigate_page`, `evaluate_script`, `take_snapshot`, `take_screenshot`, `click`, `fill`.

**ChatGPT message pattern:**
```js
// Type message
document.querySelector('.ProseMirror').focus()
document.execCommand('insertText', false, 'your message here')

// Click send
const form = document.querySelector('.ProseMirror').closest('form')
form.querySelectorAll('button').find(b => (b.getAttribute('aria-label')||'').includes('Send')).click()

// Read reply
document.body.innerText.substring(document.body.innerText.length - 2000)
```

## License

TBD
