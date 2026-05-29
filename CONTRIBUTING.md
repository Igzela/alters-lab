# Contributing to Alters Lab

Thanks for your interest in contributing! This document explains how to get started.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

The dev server proxies API requests to `http://localhost:8000`.

### Running Tests

```bash
# Backend
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q

# Frontend build check
cd apps/web && npm run build
```

## Project Structure

```
apps/
  api/          Python backend (FastAPI)
  web/          React frontend (Vite + Tailwind)
docs/           Documentation
alters/         Runtime data (YAML/JSON)
```

## Guidelines

- Keep changes focused — one feature or fix per PR
- Write tests for new backend endpoints
- Follow existing code style (no linter enforced, but stay consistent)
- Update docs if your change affects user-facing behavior

## Reporting Issues

Open a GitHub issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce (if applicable)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
