# Alters Lab

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/Igzela/alters-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Igzela/alters-lab/actions/workflows/ci.yml)

A personal future-branch simulation and calibration system. Explore potential life paths by modelling branching decisions, generating alter versions of yourself for each path, and calibrating which branches best align with your values and energy.

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
alters-lab start    # Start the server (opens browser automatically)
alters-lab open     # Open in browser (starts server if not running)
```

The app runs at `http://127.0.0.1:18790`.

### 3. Configure a Provider (Optional)

Alters Lab works out of the box with mock responses. To enable real LLM-powered dialogue and weekly reviews, configure an OpenAI-compatible provider through the in-app Provider Settings page, or via the API:

```bash
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
```

See [Provider Setup](docs/user/PROVIDER_SETUP.md) for the full guide.

## How It Works

```
Snapshot → Branches → Alters → Dialogue → Calibration
```

1. **Snapshot** — Capture your current state: constraints, uncertainties, and what you refuse to give up
2. **Branch Discovery** — Identify 3–4 structural, mutually incompatible future branches
3. **Alter Generation** — For each branch, generate an Alter: a coherent version of you living that path
4. **Dialogue** — Converse with each Alter to evaluate fit, values, and tradeoffs
5. **Calibration** — Score branches against a rubric and refine over time

## CLI Commands

| Command | Description |
|---------|-------------|
| `alters-lab start` | Start the local server |
| `alters-lab stop` | Stop the local server |
| `alters-lab status` | Show server status |
| `alters-lab doctor` | Run health checks |
| `alters-lab open` | Open the app in a browser |
| `alters-lab backup` | Create a data backup |
| `alters-lab load-sample` | Load sample data for new users |

## Sample Data

Alters Lab ships with sample data so you can explore immediately after installation:

```bash
alters-lab load-sample
```

This loads a career-change scenario with 4 branches, 4 alters, and a snapshot into `alters/current/`. The app will use this data for dialogue, calibration, and weekly reviews. Edit the files in `alters/current/` to reflect your own situation.

## Provider Modes

| Mode | Description |
|------|-------------|
| `disabled` | No LLM calls. Default out of the box. |
| `mock` | Simulated responses. For testing without an API key. |
| `openai-compatible-http` | Real LLM calls to any OpenAI-compatible API. |

## Documentation

- [First-Run Checklist](docs/user/FIRST_RUN_CHECKLIST.md) — What to do after installation
- [User Guide](docs/USER_GUIDE.md) — Quick start, workflow walkthrough, and reference
- [Provider Setup](docs/user/PROVIDER_SETUP.md) — How to configure LLM providers
- [Provider Safety](docs/user/PROVIDER_SAFETY.md) — Secret handling, output safety, confirmation gating
- [Troubleshooting](docs/user/TROUBLESHOOTING.md) — Common issues and how to fix them
- [Product Specification](docs/product-spec.md) — System design and concepts
- [Architecture](docs/architecture.md) — Technical architecture overview

## Project Structure

```
apps/
  api/              Python backend (FastAPI)
  web/              React frontend (Vite + Tailwind)
docs/               Documentation
  user/             User-facing guides
alters/             Runtime data (YAML/JSON)
  current/          Active snapshot, branches, and alters
  sample/           Sample data for new users (load via `alters-lab load-sample`)
  calibration/      Rubric, scores, and calibration state
  archive/          Completed cycle archives
```

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic, PyYAML
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS v4, TanStack Query
- **Storage:** YAML + JSON files (no database)
- **Packaging:** Debian (.deb), CLI entry point `alters-lab`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[MIT](LICENSE)
