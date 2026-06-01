# Product Positioning

## What Alters Lab Is

Alters Lab is a **public-prior + personal-calibration life trajectory forecasting system**.

It is a calibration-first personal forecasting system that combines:
- **Public priors** — population-level baselines derived from longitudinal datasets and literature
- **Personal evidence** — structured behavior metrics and weekly calibration data from the individual user
- **Locked forecast snapshots** — predictions committed before outcomes are known
- **External evidence evaluation** — real-world outcomes assessed against predictions
- **Calibration scorecard** — aggregate tracking of forecast accuracy over time

The system separates public priors, personal evidence, subjective alignment, and external outcomes into distinct layers. It improves credibility through locked forecasts and later evaluation — not through claims of individual destiny prediction.

## What Alters Lab Is Not

- **Not a deterministic life predictor** — The system does not claim to know your future. It tracks alignment between predictions and outcomes.
- **Not a trained ML model in the main app** — The main forecast system uses structured heuristics and literature priors. Any ML models live in the offline Population Baseline Lab and must pass validation gates before integration.
- **Not a probability engine by default** — Exact probabilities require calibrated model artifacts with approval. Default outputs are directional (favorable/unfavorable/mixed/unknown) with explicit transfer risk labels.
- **Not clinical / legal / financial advice** — The system is a personal reflection and calibration tool. It does not provide professional recommendations.
- **Not a social scoring system** — There is no life_score, no population_percentile unless backed by an explicit numeric baseline, and no ranking of users.
- **Not a direct deployment of FFC/NLSY/MIDUS models onto the user** — Population baselines are directional references, not individual predictions. High transfer risk is the default assumption.
- **Unknown remains unknown** — The system does not fill gaps with fabricated estimates. When evidence is insufficient, the output says so explicitly.

## Dual-Track Forecast Architecture

### Route A — Personal Evidence

- Source: user's own predictor profile, behavior metrics, weekly calibration scores
- Strengths: directly relevant to the individual
- Weaknesses: sparse data, slow accumulation, N=1 sample size
- Output: personal trajectory direction with evidence strength label

### Route B — Population Prior

- Source: literature priors (current), population baseline lab (future)
- Strengths: large samples, validated measures, established findings
- Weaknesses: population mismatch, temporal gap, ecological fallacy
- Output: prior direction with transfer risk label, no exact probabilities by default

### Hybrid Integration

Public prior and personal evidence are always displayed separately. Personal external evidence can lower or override public-prior credibility. Forecast evaluation remains the source of calibration feedback — not the population baseline.

## Validation Standard

All population priors must pass 6 validation gates before entering the forecast path. See `docs/VALIDATION_STANDARD.md` for the complete specification.

## Calibration Modules (Safety Core)

The following modules are not optional. They are the safety core that prevents the system from making unchecked claims:

1. **Forecast Snapshot** — locks predictions before outcomes are known
2. **External Evidence** — records real-world outcomes
3. **Forecast Evaluation** — compares predictions to outcomes (hit/miss/partial/unknown)
4. **Calibration Scorecard** — aggregates calibration history over time

The main forecast cannot skip the evaluation layer. Predictions that bypass calibration are disallowed by contract.
