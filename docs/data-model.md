# Data Model

All data stored as YAML/JSON under `alters/`. No database. Pydantic schemas in `apps/api/src/alters_lab/schemas/` are the truth source — this doc is a map, not a duplicate.

## Directory Structure

```
alters/
  current/                # User data (gitignored)
  sample/                 # Demo data (checked in)
  calibration/            # Rubric, scores, state
  product/                # Runtime data
    config/               # Provider config
    weekly_notes/         # Ingested weekly notes
    weekly_reviews/       # Review sessions
    calibration_records/  # Alignment scores
    pattern_reviews/      # Pattern analysis
    behavior_metrics/     # Weekly indicators
    branch_milestones/    # Milestones
    predictor_profiles/   # Trait baselines
    branch_outcome_targets/ # Outcome goals
    forecast_snapshots/   # Locked forecasts
    external_evidence/    # Real-world observations
    forecast_evaluations/ # Hit/miss tracking
    calibration_drafts/   # LLM extraction drafts
    calibration_conversations/ # LLM chat sessions
    sessions/             # Provider sessions
    exports/              # Data exports
  archive/                # Completed cycles
```

## Core Entities

**Schema files** (truth source — read the schema, not this doc):

| Entity | Schema File | Storage |
|--------|------------|---------|
| Snapshot | `schemas/snapshot.py` | `current/snapshot.yaml` |
| Branch | `schemas/branches.py` | `current/branches.yaml` |
| Alter | `schemas/alters.py` | `current/alters/alter_*.yaml` |
| Rubric | `schemas/rubric.py` | `calibration/rubric.yaml` |
| Weekly Note | `schemas/obsidian_weekly_note.py` | `product/weekly_notes/` |
| Behavior Metrics | `schemas/behavior_metrics_record.py` | `product/behavior_metrics/weekly_records/` |
| Predictor Profile | `schemas/predictor_profile.py` | `product/predictor_profiles/` |
| Outcome Target | `schemas/branch_outcome_targets.py` | `product/branch_outcome_targets/` |
| Forecast Snapshot | `schemas/forecast_snapshot.py` | `product/forecast_snapshots/` |
| External Evidence | `schemas/external_evidence.py` | `product/external_evidence/` |
| Forecast Evaluation | `schemas/forecast_evaluation.py` | `product/forecast_evaluations/` |
| Scorecard | `schemas/calibration_scorecard.py` | Computed from evaluations |
| Calibration Draft | `schemas/calibration_conversation.py` | `product/calibration_drafts/` |
| Conversation | `schemas/calibration_conversation.py` | `product/calibration_conversations/` |
| Model Card | `schemas/population_baseline.py` | `product/model_cards/` |
| Reference Artifact | `schemas/population_baseline.py` | `product/population_prior_artifacts/` |

## Forecast Pipeline Schemas

| Schema | File | Purpose |
|--------|------|---------|
| `BranchForecastResult` | `schemas/branch_forecast.py` | Full forecast with personal evidence + optional reference context + adapter |
| `ForecastSnapshotRecord` | `schemas/forecast_snapshot.py` | Locked immutable forecast record |
| `ExternalEvidenceRecord` | `schemas/external_evidence.py` | Real-world observation |
| `ForecastEvaluationRecord` | `schemas/forecast_evaluation.py` | Prediction vs outcome comparison |
| `CalibrationScorecard` | `schemas/calibration_scorecard.py` | Aggregate accuracy tracking |
| `PersonalPriorAdapterSummary` | `schemas/personal_prior_adapter.py` | Combined evidence adapter |

## LLM-Driven Calibration Schemas

| Schema | File | Purpose |
|--------|------|---------|
| `CalibrationConversation` | `schemas/calibration_conversation.py` | Chat session |
| `CalibrationDraft` | `schemas/calibration_conversation.py` | LLM extraction pending confirmation |
| `BehaviorMetricsExtract` | `schemas/calibration_conversation.py` | Behavior metrics subset for extraction |
| `ExternalEvidenceExtract` | `schemas/calibration_conversation.py` | Evidence item for extraction |
| `CalibrationScoreValues` | `schemas/calibration_loop.py` | 4-dimension rubric scores (1-5 each) |
| `RealityScoreRecord` | `schemas/calibration_loop.py` | Persisted calibration score with drift |
| `AlterRubricBaseline` | `schemas/calibration_loop.py` | Alter's predicted rubric trajectory (initial/30d/90d) |

## Population Baseline Schemas

The current schema names retain `population_baseline` for API compatibility. Public product language should describe this layer as optional external reference context rather than as a named dataset-backed prediction feature.

| Schema | File | Purpose |
|--------|------|---------|
| `PublicDatasetSource` | `schemas/population_baseline.py` | Internal source registry |
| `PopulationBaselineModelCard` | `schemas/population_baseline.py` | Model card with validation metrics |
| `PopulationPriorArtifact` | `schemas/population_baseline.py` | Reference artifact derived from an approved source/model |
| `PublicPriorIntegrationContract` | `schemas/public_prior_contract.py` | Guards for reference integration |

## Key Invariants

- `extra="forbid"` on most models — unknown fields rejected at API boundary
- Alter IDs: exactly `alter_A` through `alter_D`
- Branch refs: `alter_N` → `branch_N`
- Source refs: enforced paths (`alters/current/snapshot.yaml`, etc.)
- Rubric: `auto_modify` always `false`, changes require human approval
- No `life_score` field anywhere (enforced by tests + schema)
- No exact probability without calibrated model approval
- Third-party raw data, processed data, and offline artifacts are not product data and must not be committed or bundled by default
- `submitted_by_user: Literal[True]` on reality scores — LLM cannot auto-submit
