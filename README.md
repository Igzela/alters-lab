# Alters Lab

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/Igzela/alters-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Igzela/alters-lab/actions/workflows/ci.yml)

**Your future is not a single path. It's a branching tree of possibilities.**

Alters Lab is a **public-prior + personal-calibration life trajectory forecasting system**. It helps you explore structurally different life branches, engage in dialogue with hypothetical versions of yourself, and calibrate which paths actually align with your values — using both population-level evidence and your own weekly calibration data.

> *"We don't rise to the level of our goals, we fall to the level of our systems."* — James Clear

Alters Lab is that system.

## Why This Exists

Most decision tools ask "what do you want?" Alters Lab asks "who would you become?"

When facing a major life decision — career change, relocation, relationship, education — we tend to optimize for the wrong variables. We imagine idealized outcomes instead of mapping the real tradeoffs. Alters Lab forces you to confront those tradeoffs by generating coherent "alter" versions of yourself for each path, then calibrating your predictions against reality over time.

**The core insight:** Your future self on each branch would make different compromises, hold different values, and face different problems. Understanding those differences is more valuable than optimizing a single path.

## Key Features

### Branch Discovery
Identifies 3–4 structurally incompatible future paths. Not "slightly different versions" — fundamentally different life architectures with real tradeoffs.

### Alter Generation
For each branch, generates a coherent alter: a version of you living that path with consistent values, concerns, and decision patterns. Each alter has a distinct voice and perspective.

### Dialogue & Challenge
Converse with your alters to evaluate fit. The system includes self-deception detection — it flags when you're rationalizing instead of genuinely evaluating.

### Weekly Calibration
A structured 6-step weekly review flow:
1. **Ingest** — Paste a weekly note (freeform or template)
2. **Extract** — Structured fields: session type, observable facts, friction points
3. **Review** — Select an alter, start a review session
4. **Complete** — Write corrections, dialogue summary, next actions
5. **Score** — Rate direction alignment, execution consistency, avoidance level
6. **Analyze** — View trends, patterns, and calibration history

### Trend Analysis & Forecasting
Linear extrapolation from historical scores with confidence intervals. See where your trajectory is heading — improving, declining, or stable — with per-dimension breakdowns.

### Pattern Detection
Identifies repeated behavioral patterns across weeks:
- **Noisy Progress** — Activity without meaningful progress
- **Avoidance Disguised as Work** — Doing easy tasks to avoid hard ones
- **Sleep Breakdown** — Energy management issues
- **Over Scope** — Taking on too much
- **Action Mismatch** — Actions don't match stated intentions

### Dynamic Rubric Weights
Automatically adjusts evaluation emphasis based on your current state. Low alignment? The system emphasizes execution discipline. High alignment? It opens up exploration freedom.

### Data Safety First
- **Local-only** — Runs on `127.0.0.1:18790`. No cloud, no external calls unless you configure them.
- **YAML on disk** — All data is readable, editable, version-controllable files. No database.
- **User-driven scoring** — The system never infers your scores. You submit them explicitly.
- **Advisory algorithms** — Trend analysis, pattern detection, and weight adjustments are evidence. They never trigger automatic actions.
- **No life_score** — The system does not produce a single number representing your life quality.
- **No exact probability** — Directional forecasts only, with explicit transfer risk labels.

### Route B — Population Priors
Population-level baselines from longitudinal datasets (NLSY97, MIDUS) inform forecasts across 5 life domains:
- **career_education** / **financial** — strong_calibrated (NLSY97 calibrated models)
- **health** / **subjective_wellbeing** — data_backed (MIDUS baselines)
- **relationship** — contextual (literature prior)

### Personal Prior Adapter
Combines Route A (personal evidence), Route B (population priors), and external evidence into per-domain adjusted forecasts. Surfaces conflicts between sources for human judgment. Not a destiny prediction — a decision-support layer.

## Quick Start

### 1. Install

**Docker** (recommended):

```bash
git clone https://github.com/Igzela/alters-lab.git
cd alters-lab
docker compose up -d
# Open http://localhost:18790
```

**From source**:

```bash
git clone https://github.com/Igzela/alters-lab.git
cd alters-lab
python3 -m venv .venv && source .venv/bin/activate
pip install -e "apps/api[dev]"
cd apps/web && npm install && cd ../..
alters-lab start
```

> **Linux/macOS users**: If `pip install` fails with "externally-managed-environment", you must use a virtualenv (shown above). On Windows, `pip install` works directly.

**Development mode** (hot-reload frontend):

```bash
source .venv/bin/activate
PYTHONPATH=apps/api/src uvicorn alters_lab.main:app --port 18790 &
cd apps/web && npm run dev
# Frontend: http://localhost:5173  Backend: http://localhost:18790
```

### 2. Load Sample Data

```bash
alters-lab load-sample
```

This loads a career-change scenario with 4 branches, 4 alters, and a snapshot. Explore the system immediately, then edit `alters/current/` to reflect your own situation.

### 3. Explore

- **Dashboard** — See your calibration status at a glance
- **Weekly Review** — Run through the 6-step flow with sample data
- **Alter Dialogue** — Chat with your alters about their paths
- **Calibration History** — View trends and pattern detection
- **Public Priors** — View Route B domain coverage and model cards
- **Branch Forecast** — See Route A / Route B / Adapter combined forecasts

### 4. Configure a Provider (Optional)

Alters Lab works out of the box with mock responses. For real LLM-powered dialogue:

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
Snapshot → Branch Discovery → Alter Generation → Dialogue → Calibration
    ↓                                                         ↓
    └──────────── Reality Score ←──── Weekly Reviews ←──────────┘
```

1. **Snapshot** — Capture your current state: heaviest constraint, most unclear direction, what you refuse to give up
2. **Branch Discovery** — Identify 3–4 structural, mutually incompatible future branches
3. **Alter Generation** — For each branch, generate an Alter: a coherent version of you living that path
4. **Dialogue** — Converse with each Alter to evaluate fit, values, and tradeoffs
5. **Calibration** — Score branches against a 4-dimension rubric (execution discipline, exploration freedom, life state match, energy level) and refine over time through weekly review cycles

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Alters Lab                           │
├─────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript + Tailwind)               │
│  ├── Dashboard (trend charts, status overview)          │
│  ├── Weekly Review (6-step calibration flow)            │
│  ├── Alter Dialogue (chat with your alters)             │
│  ├── Calibration History (trends, patterns, scores)     │
│  ├── Public Priors (Route B coverage, model cards)      │
│  ├── Branch Forecast (Route A + B + Adapter)            │
│  └── 15 pages total                                     │
├─────────────────────────────────────────────────────────┤
│  Backend (Python + FastAPI + Pydantic)                  │
│  ├── 47 API routers                                     │
│  ├── 54 service modules                                 │
│  ├── 49 Pydantic schema modules                         │
│  ├── Route B: population priors (NLSY97 + MIDUS)        │
│  ├── Personal Prior Adapter                             │
│  └── Pattern detection, trend analysis, dynamic weights │
├─────────────────────────────────────────────────────────┤
│  Storage (YAML + JSON files)                            │
│  ├── alters/current/    Active user data                │
│  ├── alters/sample/     Demo data for new users         │
│  ├── alters/product/    Weekly reviews, calibration     │
│  │   ├── forecast_snapshots/  Locked forecasts          │
│  │   ├── external_evidence/   Real-world observations   │
│  │   ├── forecast_evaluations/ Hit/miss tracking        │
│  │   └── predictor_profiles/  User trait baselines      │
│  └── alters/calibration Rubric, scores, state           │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Pydantic v2, PyYAML |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4 |
| Data Layer | TanStack Query (React Query) |
| Charts | Recharts |
| Icons | Phosphor Icons |
| Fonts | Outfit (body), JetBrains Mono (code) |
| i18n | English + Chinese |
| Storage | YAML + JSON files (no database) |
| Packaging | Debian `.deb`, Docker |
| Routing | React Router v6 |
| Tests | pytest (1931 backend), vitest (81 frontend) |

## CLI Commands

| Command | Description |
|---------|-------------|
| `alters-lab start` | Start the local server (opens browser) |
| `alters-lab stop` | Stop the local server |
| `alters-lab status` | Show server status |
| `alters-lab doctor` | Run health checks |
| `alters-lab open` | Open in browser |
| `alters-lab backup` | Create a data backup |
| `alters-lab load-sample` | Load sample data for new users |

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
- [Product Positioning](docs/PRODUCT_POSITIONING.md) — What Alters Lab is and is not
- [Validation Standard](docs/VALIDATION_STANDARD.md) — Population prior integration gates
- [Product Specification](docs/product-spec.md) — System design and concepts
- [Architecture](docs/architecture.md) — Technical architecture overview
- [Data Model](docs/data-model.md) — Schema definitions and invariants

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/alters-lab.git`
3. **Install** dependencies:
   ```bash
   pip install -e "apps/api[dev]"
   cd apps/web && npm install
   ```
4. **Run tests**:
   ```bash
   # Backend
   PYTHONPATH=apps/api/src pytest apps/api/tests/ -q
   # Frontend
   cd apps/web && npm run test
   ```
5. **Create a branch** for your feature: `git checkout -b feature/my-feature`
6. **Commit** your changes: `git commit -m "feat: add my feature"`
7. **Push** and open a **Pull Request**

### Development Priorities

We're actively working on:
- **P6 Validation** — Collecting 21+ days of evidence for behavior validation
- **UI Polish** — Mobile responsiveness, accessibility improvements
- **Pattern Analysis** — Better detection algorithms, cross-pattern correlations
- **Export & Reporting** — PDF reports, data visualization improvements
- **Multi-language** — More language support beyond English and Chinese

### Good First Issues

Looking for a way to contribute? Check issues labeled `good-first-issue` for tasks that are approachable for newcomers.

## Roadmap

- [x] Route B population priors (NLSY97 + MIDUS, all 5 domains)
- [x] Personal Prior Adapter (combines Route A + B + external evidence)
- [x] Forecast snapshots, evaluations, scorecard with per-source tracking
- [ ] Real user pilot (4-8 weeks of calibration data)
- [ ] P6 behavior validation gate (collecting evidence)
- [ ] Relationship domain calibrated model (currently contextual only)
- [ ] Mobile-responsive navigation improvements
- [ ] PDF export for calibration reports
- [ ] Accessibility audit and improvements

## License

[MIT](LICENSE) — Use it, modify it, distribute it. Just keep the license notice.

## Acknowledgments

Built with ❤️ as a personal tool for navigating life's branching decisions. If it helps you make better choices, that's the whole point.
