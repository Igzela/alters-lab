# Development Setup

Complete guide to running Alters Lab locally for development.

## Prerequisites

| Tool    | Version   | Check command       |
|---------|-----------|---------------------|
| Python  | 3.11+     | `python3 --version` |
| Node.js | 18+       | `node --version`    |
| npm     | 9+        | `npm --version`     |
| Git     | 2.30+     | `git --version`     |

Optional:
- Docker + Docker Compose (for containerised builds)
- A keyring-compatible OS (GNOME Keyring, macOS Keychain) for LLM API key storage

## Repository Layout

```
alters-lab/
  apps/
    api/          # FastAPI backend (Python)
    web/          # React frontend (TypeScript + Vite)
  alters/
    sample/       # Sample data shipped with the product
    product/      # Product config, schemas, rubrics
  docs/           # Documentation
  Dockerfile
  docker-compose.yml
```

---

## Backend Setup (FastAPI)

### 1. Create a virtual environment

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

This installs the runtime dependencies (fastapi, pydantic, pyyaml, uvicorn) plus dev extras (pytest, httpx).

To also install the optional `pyreadstat` dependency (used by the lab module for SPSS/SAS file reading):

```bash
pip install -e ".[dev,lab]"
```

### 3. Set PYTHONPATH

All commands assume `PYTHONPATH` points to the source tree:

```bash
export PYTHONPATH=apps/api/src
```

### 4. Environment variables

The backend reads configuration from environment variables and a YAML config file. No `.env` file is required for basic development. Key variables:

| Variable                  | Purpose                                     | Default      |
|---------------------------|---------------------------------------------|--------------|
| `ALTERS_LAB_MODE`         | `dev` (local) or `packaged` (Docker/deb)    | (unset = dev)|
| `ALTERS_LAB_APP_ROOT`     | Path to app install (packaged mode only)    | —            |
| `ALTERS_PROVIDER_MODE`    | `disabled`, `mock`, or `openai_compatible_http` | `mock`   |
| `ALTERS_PROVIDER_BASE_URL`| LLM API base URL                            | —            |
| `ALTERS_PROVIDER_API_KEY` | LLM API key                                 | —            |
| `ALTERS_PROVIDER_MODEL`   | Model name                                  | `mock-model` |

For local development without an LLM, the default `mock` provider mode is sufficient. See [Provider Configuration](PROVIDER_CONFIGURATION.md) for real LLM setup.

### 5. Run the backend

```bash
PYTHONPATH=apps/api/src python3 -m uvicorn alters_lab.main:app --host 127.0.0.1 --port 18790 --reload
```

The API is available at `http://127.0.0.1:18790`. OpenAPI docs at `http://127.0.0.1:18790/docs`.

---

## Frontend Setup (React + Vite)

### 1. Install dependencies

```bash
cd apps/web
npm install
```

### 2. Run the dev server

```bash
npm run dev
```

Vite starts on `http://localhost:5173` by default. API requests are proxied to the backend at `http://localhost:18790` (configured in `vite.config.ts`). The backend must be running for API calls to work.

### 3. Type generation (optional)

If you change the backend API schema and need updated TypeScript types:

```bash
npm run generate:types
```

This runs the backend's OpenAPI export script, then generates `src/api-types.ts`.

---

## Docker Setup

Build and run the full stack in a single container:

```bash
docker compose up --build
```

This:
1. Builds the frontend (`npm run build`)
2. Creates a Python 3.11 runtime image
3. Copies the frontend build into the backend's static serving path
4. Starts uvicorn on port `18790`

Access at `http://localhost:18790`. Data persists in a Docker volume (`alters-data`).

To run in the background:

```bash
docker compose up -d --build
```

To stop and remove volumes:

```bash
docker compose down -v
```

---

## Testing

### Backend tests (pytest)

```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q
```

Run a specific test file:

```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/test_alter_dialogue.py -q
```

Run with verbose output:

```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -v
```

The test suite has ~1970 tests. A full run takes under 30 seconds.

### Frontend tests (vitest)

```bash
cd apps/web
npm run test
```

Run in watch mode during development:

```bash
npm run test:watch
```

The frontend has ~84 tests.

### Full build check

```bash
cd apps/web
npm run build
```

This runs TypeScript type-checking (`tsc -b`) and Vite production build. Any type errors will fail the build.

---

## Linting

### Python (ruff)

If ruff is installed (`pip install ruff`):

```bash
ruff check apps/api/src/
ruff format apps/api/src/
```

### TypeScript (tsc)

Type checking is included in the build step:

```bash
cd apps/web && npx tsc -b --noEmit
```

Or simply run `npm run build` which includes `tsc -b`.

---

## Common Issues

### `ModuleNotFoundError: No module named 'alters_lab'`

You forgot to set `PYTHONPATH`. Run:

```bash
export PYTHONPATH=apps/api/src
```

Or prefix every command with `PYTHONPATH=apps/api/src`.

### Backend starts but frontend shows network errors

The frontend dev server must proxy to a running backend. Make sure the backend is running on port 18790 before opening the frontend.

### `EADDRINUSE: address already in use 18790`

Another process is using the port. Find and kill it:

```bash
lsof -i :18790
kill <PID>
```

### `pip install` fails with build errors

Ensure you have Python 3.11+ and a recent pip:

```bash
python3 --version   # must be 3.11+
pip install --upgrade pip
```

### npm install fails or hangs

Clear the cache and retry:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Provider features return mock responses

This is the default. The provider mode is `mock` unless you configure it. See [Provider Configuration](PROVIDER_CONFIGURATION.md) to connect a real LLM.

### Docker build fails on frontend stage

Ensure `apps/web/package-lock.json` exists. If not:

```bash
cd apps/web && npm install   # generates package-lock.json
```

Then retry the Docker build.

---

## IDE Setup (VS Code)

### Recommended extensions

| Extension                   | Purpose                          |
|-----------------------------|----------------------------------|
| `ms-python.python`         | Python language support           |
| `ms-python.vscode-pylance` | Type checking and IntelliSense   |
| `charliermarsh.ruff`       | Python linting and formatting    |
| `dbaeumer.vscode-eslint`   | TypeScript/React linting         |
| `bradlc.vscode-tailwindcss`| Tailwind CSS IntelliSense        |
| `esbenp.prettier-vscode`   | Code formatting                  |

### Workspace settings

Create `.vscode/settings.json` in the project root:

```json
{
  "python.defaultInterpreterPath": "apps/api/.venv/bin/python",
  "python.analysis.extraPaths": ["apps/api/src"],
  "typescript.tsdk": "apps/web/node_modules/typescript/lib",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier"
  }
}
```

### Launch configurations

Create `.vscode/launch.json` for debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend (uvicorn)",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["alters_lab.main:app", "--host", "127.0.0.1", "--port", "18790", "--reload"],
      "cwd": "${workspaceFolder}/apps/api/src",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/apps/api/src"
      }
    }
  ]
}
```

---

## Quick Start (TL;DR)

```bash
# Terminal 1 — Backend
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=apps/api/src python3 -m uvicorn alters_lab.main:app --host 127.0.0.1 --port 18790 --reload

# Terminal 2 — Frontend
cd apps/web
npm install
npm run dev
```

Open `http://localhost:5173`.
