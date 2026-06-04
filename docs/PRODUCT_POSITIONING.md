# Product Positioning

## What Alters Lab Is

Alters Lab is a **public-prior + personal-calibration life trajectory forecasting system**.

It is a calibration-first personal forecasting system that combines:
- **Public priors** — population-level baselines derived from longitudinal datasets (NLSY97, MIDUS)
- **Personal evidence** — structured behavior metrics and weekly calibration data from the individual user
- **Personal Prior Adapter** — decision-support layer that combines Route A, Route B, and external evidence into adjusted per-domain forecasts
- **Locked forecast snapshots** — predictions committed before outcomes are known
- **External evidence evaluation** — real-world outcomes assessed against predictions
- **Calibration scorecard** — aggregate tracking of forecast accuracy over time, with per-source hit rates

The system separates public priors, personal evidence, subjective alignment, and external outcomes into distinct layers. It improves credibility through locked forecasts and later evaluation — not through claims of individual destiny prediction.

## What Alters Lab Is Not

- **Not a deterministic life predictor** — The system does not claim to know your future. It tracks alignment between predictions and outcomes.
- **Not a trained ML model in the main app** — The main forecast system uses structured heuristics and literature priors. Any ML models live in the offline Population Baseline Lab and must pass validation gates before integration.
- **Not a probability engine by default** — Exact probabilities require calibrated model artifacts with approval. Default outputs are directional (improving/declining/stable/mixed/unknown) with explicit transfer risk labels.
- **Not a life scoring system** — There is no life_score. The system does not produce a single number that represents your life quality.
- **Not clinical / legal / financial advice** — The system is a personal reflection and calibration tool. It does not provide professional recommendations.
- **Not a social scoring system** — There is no life_score, no population_percentile unless backed by an explicit numeric baseline, and no ranking of users.
- **Not a direct deployment of NLSY/MIDUS models onto the user** — Population baselines are directional references, not individual predictions. High transfer risk is the default assumption for mismatched populations.
- **Unknown remains unknown** — The system does not fill gaps with fabricated estimates. When evidence is insufficient, the output says so explicitly.

## Dual-Track Forecast Architecture

### Route A — Personal Evidence

- Source: user's own predictor profile, behavior metrics, weekly calibration scores
- Strengths: directly relevant to the individual
- Weaknesses: sparse data, slow accumulation, N=1 sample size
- Output: personal trajectory direction with evidence strength label

### Route B — Population Prior

- Source: calibrated public baseline models (NLSY97 for career/financial, MIDUS for health/wellbeing) and contextual priors (relationship)
- Strengths: large samples, validated measures, established findings
- Weaknesses: population mismatch, temporal gap, ecological fallacy
- Output: prior direction with transfer risk label and strength level (strong_calibrated / data_backed / contextual / none)

#### Strength Levels

| Level | Meaning | Domains |
|-------|---------|---------|
| `strong_calibrated` | Calibrated model with out-of-sample metrics, approved for Route B | career_education, financial |
| `data_backed` | Data-backed baseline with aggregate statistics, approved for Route B | health, subjective_wellbeing |
| `contextual` | Literature or weak prior, not approved for Route B | relationship |
| `none` | No prior available | — |

### Personal Prior Adapter

The adapter is a **decision-support layer** that combines all three evidence sources:

1. **Route A direction** — what personal behavior data suggests
2. **Route B direction** — what population priors suggest
3. **External evidence** — what real-world observations indicate

Per domain, the adapter computes:
- **Alignment** — are the sources agreeing or conflicting?
- **Conflict level** — how much disagreement exists?
- **Adjusted direction** — the combined forecast direction
- **Adjusted confidence** — how confident should we be?
- **Readiness** — is there enough evidence to make a forecast?

Key rules:
- External evidence can override weak Route B
- Strong Route A can reduce pessimism from Route B but cannot erase transfer risk
- `strong_calibrated` Route B increases confidence when aligned with Route A
- `contextual` prior cannot drive adjusted direction
- Missing or stale behavior data lowers forecast readiness

**The adapter is not destiny prediction.** It is a structured way to combine available evidence and surface conflicts for human judgment.

### Route A + Route B + Adapter in Evaluation

Forecast evaluation tracks match results separately for each source:
- `route_a_match_result` — how Route A alone would have done
- `route_b_match_result` — how Route B alone would have done
- `adapter_match_result` — how the combined result did

This enables understanding which evidence source is most predictive for each domain.

## Validation Standard

All population priors must pass 6 validation gates before entering the forecast path. See `docs/VALIDATION_STANDARD.md` for the complete specification.

## Calibration Modules (Safety Core)

The following modules are not optional. They are the safety core that prevents the system from making unchecked claims:

1. **Forecast Snapshot** — locks predictions before outcomes are known, preserving adapter results
2. **External Evidence** — records real-world outcomes with structured fields
3. **Forecast Evaluation** — compares predictions to outcomes (hit/miss/partial/unknown), per source
4. **Calibration Scorecard** — aggregates calibration history with Route A / Route B / Adapter hit rates

The main forecast cannot skip the evaluation layer. Predictions that bypass calibration are disallowed by contract.

## What Remains Experimental

- Population Baseline Lab (offline analysis scripts, not runtime ML)
- SQLite repository backend (code exists, YAML is active backend)
- Relationship domain (contextual prior only, no calibrated model)
- P6 behavior validation (collecting evidence, not yet sealed)
