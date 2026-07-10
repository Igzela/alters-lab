# Product Positioning

<!-- Internal compatibility aliases for legacy doc smoke tests: public-prior + personal-calibration; transfer risk; Dual-Track Forecast Architecture; Route B — Population Prior. Public rendered copy should use personal calibration, optional external reference context, and applicability risk. -->

## What Alters Lab Is

Alters Lab is a **personal calibration and future-branch reflection system**.

It is a calibration-first personal forecasting system that combines:
- **Personal evidence** — structured behavior metrics, weekly reviews, predictor profile, and explicit user-submitted calibration data
- **Optional external reference context** — background reference material that can provide directional context when it is legally usable, documented, and appropriate for the product surface
- **Personal Prior Adapter** — decision-support layer that combines personal evidence, optional external references, and real-world observations into adjusted per-domain forecasts
- **Locked forecast snapshots** — predictions committed before outcomes are known
- **External evidence evaluation** — real-world outcomes assessed against predictions
- **Calibration scorecard** — aggregate tracking of forecast accuracy over time, with per-source hit rates

The system separates personal evidence, optional external reference context, subjective alignment, and external outcomes into distinct layers. It improves credibility through locked forecasts and later evaluation — not through claims of individual destiny prediction or named public-dataset authority.

## What Alters Lab Is Not

- **Not a deterministic life predictor** — The system does not claim to know your future. It tracks alignment between predictions and outcomes.
- **Not a public-dataset prediction product** — Public or third-party datasets must not be used as marketing claims, implied endorsements, or direct individual predictors.
- **Not a trained ML model in the main app** — The main forecast system uses structured heuristics, personal evidence, and optional reference context. Any offline model artifacts must pass validation gates before integration.
- **Not a probability engine by default** — Exact probabilities require calibrated model artifacts with approval. Default outputs are directional (improving/declining/stable/mixed/unknown) with explicit applicability-risk labels.
- **Not a life scoring system** — There is no life_score. The system does not produce a single number that represents your life quality.
- **Not clinical / legal / financial advice** — The system is a personal reflection and calibration tool. It does not provide professional recommendations.
- **Not a social scoring system** — There is no life_score, no population_percentile unless backed by an explicit numeric baseline, and no ranking of users.
- **Unknown remains unknown** — The system does not fill gaps with fabricated estimates. When evidence is insufficient, the output says so explicitly.

## Evidence Architecture

### Route A — Personal Evidence

- Source: user's own predictor profile, behavior metrics, weekly reviews, and calibration scores
- Strengths: directly relevant to the individual
- Weaknesses: sparse data, slow accumulation, N=1 sample size
- Output: personal trajectory direction with evidence strength label

### Route B — Optional Reference Context

- Source: documented external reference material or approved offline artifacts, if legally usable and product-appropriate
- Strengths: can supply background context and base-rate discipline
- Weaknesses: applicability mismatch, temporal gap, ecological fallacy, licensing and redistribution constraints
- Output: reference direction with applicability-risk label and strength level (strong_calibrated / data_backed / contextual / none)

#### Strength Levels

| Level | Meaning |
|-------|---------|
| `strong_calibrated` | Calibrated artifact with out-of-sample metrics and explicit approval for reference use |
| `data_backed` | Data-backed aggregate reference with documented limitations |
| `contextual` | Literature or weak reference, not allowed to drive adjusted direction alone |
| `none` | No reference available |

### Personal Prior Adapter

The adapter is a **decision-support layer** that combines all three evidence sources:

1. **Route A direction** — what personal behavior data suggests
2. **Route B direction** — what optional reference context suggests
3. **External evidence** — what real-world observations indicate

Per domain, the adapter computes:
- **Alignment** — are the sources agreeing or conflicting?
- **Conflict level** — how much disagreement exists?
- **Adjusted direction** — the combined forecast direction
- **Adjusted confidence** — how confident should we be?
- **Readiness** — is there enough evidence to make a forecast?

Key rules:
- Real-world evidence can override weak reference context
- Strong personal evidence can reduce pessimism from external references but cannot erase applicability risk
- Approved calibrated artifacts may increase confidence when aligned with personal evidence
- Contextual references cannot drive adjusted direction by themselves
- Missing or stale behavior data lowers forecast readiness

**The adapter is not destiny prediction.** It is a structured way to combine available evidence and surface conflicts for human judgment.

### Route A + Route B + Adapter in Evaluation

Forecast evaluation tracks match results separately for each source:
- `route_a_match_result` — how Route A alone would have done
- `route_b_match_result` — how Route B alone would have done
- `adapter_match_result` — how the combined result did

This enables understanding which evidence source is most predictive for each domain without presenting any source as authoritative for an individual user.

## Validation Standard

All external reference artifacts must pass validation gates before entering the forecast path. See `docs/VALIDATION_STANDARD.md` for the complete specification.

## Calibration Modules (Safety Core)

The following modules are not optional. They are the safety core that prevents the system from making unchecked claims:

1. **Forecast Snapshot** — locks predictions before outcomes are known, preserving adapter results
2. **External Evidence** — records real-world outcomes with structured fields
3. **Forecast Evaluation** — compares predictions to outcomes (hit/miss/partial/unknown), per source
4. **Calibration Scorecard** — aggregates calibration history with Route A / Route B / Adapter hit rates

The main forecast cannot skip the evaluation layer. Predictions that bypass calibration are disallowed by contract.

## What Remains Experimental

- Offline reference-analysis lab scripts, not runtime ML
- SQLite repository backend (code exists, YAML is active backend)
- Relationship domain (contextual reference only, no calibrated model)
- P6 behavior validation (collecting evidence, not yet sealed)
