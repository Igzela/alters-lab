# Contributing to Alters Lab

Thank you for your interest in contributing! This document explains how to get started.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/Igzela/alters-lab.git
cd alters-lab

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e "apps/api[dev]"
```

### Frontend Setup

```bash
cd apps/web
npm install
```

### Running Tests

```bash
# Backend tests (1291 tests)
PYTHONPATH=apps/api/src pytest apps/api/tests/ -q

# Frontend tests (12 tests)
cd apps/web && npm run test
```

### Running the App

```bash
# Start the server
alters-lab start

# Or run backend and frontend separately
PYTHONPATH=apps/api/src uvicorn alters_lab.main:app --reload --port 8000
cd apps/web && npm run dev
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Pydantic models with `extra="forbid"` for API schemas
- Services are stateless functions, not classes
- Tests use `tmp_path` fixture, never modify real files

### TypeScript/React

- Functional components with hooks
- TanStack Query for data fetching
- Tailwind CSS for styling
- i18n for all user-facing text

## Architecture

- **Schemas** (`apps/api/src/alters_lab/schemas/`) — Pydantic models, no business logic
- **Services** (`apps/api/src/alters_lab/services/`) — Business logic, stateless functions
- **API** (`apps/api/src/alters_lab/api/`) — FastAPI routers, thin wrappers
- **Pages** (`apps/web/src/pages/`) — React page components
- **Components** (`apps/web/src/components/`) — Shared UI components
- **Hooks** (`apps/web/src/hooks/`) — TanStack Query hooks

## Safety Rules

These are hard boundaries — do not violate:

1. **No active YAML modification** — Never write to `alters/current/` from code
2. **No probability forecasting** — Trend analysis is descriptive, not predictive
3. **User-driven scoring** — Reality scores require explicit user submission
4. **Advisory only** — Dynamic weights and pattern adjustments never auto-apply
5. **No database** — All storage is YAML/JSON files on disk

## Pull Request Guidelines

1. Keep PRs focused — one feature or fix per PR
2. Include tests for new functionality
3. Update documentation if needed
4. Ensure all tests pass before submitting
5. Write clear commit messages explaining *why*, not just *what*

## Issues

- Use GitHub Issues for bug reports and feature requests
- Check existing issues before creating new ones
- Label issues appropriately (bug, enhancement, documentation, good-first-issue)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
