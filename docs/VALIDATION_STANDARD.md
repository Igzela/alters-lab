# Validation Standard — Population Prior Integration

This document defines the 6 validation gates that any population baseline must pass before entering the main Alters Lab forecast system.

## Gate 1 — Public Data Traceability

**PASS requires:**
- Every public baseline must name its dataset/source
- Every outcome must have an explicit definition
- Every feature must have a mapping from source variables to internal fields
- Every model artifact must have a model card
- Every prior must carry a transfer_risk label

**FAIL if:**
- An unnamed dataset is used as a baseline
- An outcome has no operational definition
- A feature is used without mapping documentation
- A model artifact lacks a model card
- A prior has no transfer_risk label

## Gate 2 — Model Calibration

**PASS requires:**
- No model enters the forecast path without out-of-sample evaluation
- Model card must include calibration metrics when probabilities are used (brier_score, calibration_slope, calibration_intercept, auc)
- Accuracy alone is insufficient — calibration slope and intercept are required
- If sample transfer risk is high, confidence must be capped at medium or below

**FAIL if:**
- A model with `training_status = not_trained` produces numeric priors
- A model card lacks calibration metrics but emits probability bands
- Transfer risk is high but confidence is set to high

## Gate 3 — Transfer Risk

**PASS requires:**
- Public-prior output must label population mismatch
- FFCWS-like samples (specific, non-representative cohorts) must be marked high transfer risk by default
- Public priors must not be called individual predictions

**FAIL if:**
- A prior claims to be "your probability" or "your outcome likelihood"
- A high-transfer-risk dataset is presented as low risk
- Population-level associations are stated as individual-level predictions

## Gate 4 — Hybrid Integration

**PASS requires:**
- Public prior and personal evidence are displayed separately in the forecast output
- Personal external evidence can lower or override public-prior credibility
- Forecast evaluation remains the source of calibration feedback (not the population baseline)

**FAIL if:**
- Public prior overrides personal evidence without explicit user action
- Population baseline output replaces forecast evaluation as the calibration source
- The system presents a blended score without distinguishing sources

## Gate 5 — No False Precision

**PASS requires:**
- No life_score — the system does not produce a single life quality number
- No exact probability unless explicitly backed by a calibrated model artifact with `approved_for_route_b = true`
- No population_percentile unless an explicit numeric baseline exists
- Unknown remains unknown — the system does not fill gaps with estimates
- overall_fallback remains clearly marked when evidence is insufficient

**FAIL if:**
- A life_score field appears anywhere in the output
- An exact probability is emitted without a validated model card
- A population_percentile is computed without a numeric baseline
- Unknown states are filled with default estimates

## Gate 6 — Calibration Module Preserved

**PASS requires:**
- Forecasts can be locked as snapshots (ForecastSnapshotRecord)
- External evidence can be recorded (ExternalEvidenceRecord)
- Forecast evaluations produce hit/miss/partial/unknown results (ForecastEvaluationRecord)
- Scorecard aggregates calibration history (CalibrationScorecard)
- Main forecast cannot skip the evaluation layer

**FAIL if:**
- A forecast bypasses the snapshot mechanism
- External evidence recording is disabled
- Evaluation produces results other than hit/miss/partial/unknown
- Scorecard is not updated after evaluation
- The forecast path skips evaluation entirely

## Contract Enforcement

The `PublicPriorIntegrationContract` schema (in `apps/api/src/alters_lab/schemas/public_prior_contract.py`) encodes these gates as machine-readable guards and disallowed behaviors. Any integration code must validate against this contract before allowing population priors into the forecast path.
