# Population Baseline Lab

## Purpose

The Population Baseline Lab is an **offline, research-only** module for developing auditable population baseline priors. These priors can eventually feed into the main Alters Lab forecast system via Route B — but only after passing the validation gates defined in `docs/VALIDATION_STANDARD.md`.

## What This Lab Does

- Defines schemas for public datasets, outcome definitions, feature mappings, and model cards
- Provides example configurations for known longitudinal datasets (NLSY, MIDUS, PSID, FFCWS)
- Documents how public data sources map to the 5-domain Alters Lab system
- Establishes a model card template for auditability

## What This Lab Does NOT Do

- Does NOT train production ML models
- Does NOT download datasets automatically
- Does NOT emit individual predictions
- Does NOT bypass the forecast snapshot / external evidence / evaluation / scorecard pipeline
- Does NOT run inside the main FastAPI app

## Architecture Position

```
Public Data / Literature
        │
        ▼
Population Baseline Lab (this module)
        │
        ▼  [must pass validation gates]
PopulationPriorArtifact
        │
        ▼  [requires approved model card + contract]
Route B in main forecast system
        │
        ▼
Forecast Snapshot → External Evidence → Evaluation → Scorecard
```

## Validation Gates

Before any population prior enters the main forecast path, it must pass all 6 gates defined in `docs/VALIDATION_STANDARD.md`:

1. **Gate 1 — Public data traceability**: Every baseline must name its source
2. **Gate 2 — Model calibration**: No model enters forecast path without out-of-sample evaluation
3. **Gate 3 — Transfer risk**: Public priors must be labeled with population mismatch risk
4. **Gate 4 — Hybrid integration**: Public priors and personal evidence displayed separately
5. **Gate 5 — No false precision**: No exact probabilities without calibrated model artifacts
6. **Gate 6 — Calibration module preserved**: Forecast snapshots, evidence, evaluation, scorecard remain mandatory

## Schema Location

All schemas live in `apps/api/src/alters_lab/schemas/population_baseline.py`. The integration contract lives in `apps/api/src/alters_lab/schemas/public_prior_contract.py`.

## Configuration Files

- `config/example_dataset_registry.yaml` — Example dataset source definitions
- `config/example_feature_mapping.yaml` — Example feature-to-predictor mappings
- `config/example_outcome_definitions.yaml` — Example outcome definitions per domain
- `model_card_template.md` — Template for creating model cards

## Current Status

Phase 11 — Scaffold only. No real models trained, no datasets downloaded, no production integration. The lab exists to define the contract and validation standard before any ML work begins.
