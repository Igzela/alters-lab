# Validation Standard — External Reference Integration

<!-- Internal compatibility aliases for legacy doc smoke tests: Population Prior Integration; Public Data Traceability; Transfer Risk. Public rendered copy should use external reference integration, source traceability, and applicability risk. -->

This document defines the validation gates that any external reference artifact must pass before entering the main Alters Lab forecast system.

**v1.0-rc status:** The reference layer is treated as optional context, not as a product claim or direct individual prediction source. Public or third-party datasets must not be named in marketing copy, bundled as source files, or presented as official endorsement.

## Gate 1 — Source Traceability

**PASS requires:**
- Every reference artifact must name its source internally
- Every outcome must have an explicit definition
- Every feature must have a mapping from source variables to internal fields
- Every model artifact must have a model card
- Every reference output must carry an applicability-risk label
- Source terms must be reviewed before distribution or commercial use

**FAIL if:**
- An unnamed source is used as a baseline
- An outcome has no operational definition
- A feature is used without mapping documentation
- A model artifact lacks a model card
- A reference output has no applicability-risk label
- Raw, processed, or derived restricted files are committed or bundled with the product without explicit permission

**v1.0-rc status:** ✅ PASS for the internal contract design. Public distribution must continue to exclude raw data, processed data, and offline artifacts unless their source terms explicitly allow that use.

## Gate 2 — Model Calibration

**PASS requires:**
- No model enters the forecast path without out-of-sample evaluation
- Model card must include calibration metrics when probabilities are used (brier_score, calibration_slope, calibration_intercept, auc)
- Accuracy alone is insufficient — calibration slope and intercept are required
- If sample applicability risk is high, confidence must be capped at medium or below

**FAIL if:**
- A model with `training_status = not_trained` produces numeric priors
- A model card lacks calibration metrics but emits probability bands
- Applicability risk is high but confidence is set to high
- A public reference is presented as a user's personal probability without an approved calibrated artifact

**v1.0-rc status:** ✅ PASS for guardrail design. Calibrated artifacts remain internal and must not be promoted as public-dataset-backed personal prediction claims.

## Gate 3 — Applicability Risk

**PASS requires:**
- Reference output must label population, context, and time mismatch when relevant
- Narrow or non-representative samples must be marked high applicability risk by default
- External references must not be called individual predictions

**FAIL if:**
- A reference claims to be "your probability" or "your outcome likelihood"
- A high-risk source is presented as low risk
- Group-level associations are stated as individual-level predictions
- Named data sources are used as commercial proof points or implied endorsements

**v1.0-rc status:** ✅ PASS — All domain predictions carry applicability-risk labels. Strength levels (strong_calibrated > data_backed > contextual > none) reflect evidence quality.

## Gate 4 — Hybrid Integration

**PASS requires:**
- External reference context and personal evidence are displayed separately in the forecast output
- Personal external evidence can lower or override reference credibility
- Forecast evaluation remains the source of calibration feedback, not the reference layer

**FAIL if:**
- External references override personal evidence without explicit user action
- Reference output replaces forecast evaluation as the calibration source
- The system presents a blended score without distinguishing sources
- External references are used when licensing, attribution, or redistribution terms are unresolved

**v1.0-rc status:** ✅ PASS — Personal evidence, optional reference context, and external evidence are represented as separate components. Per-source match results are tracked in evaluation.

## Gate 5 — No False Precision

**PASS requires:**
- No life_score — the system does not produce a single life quality number
- No exact probability unless explicitly backed by a calibrated model artifact with approval
- No population_percentile unless an explicit numeric baseline exists and is legally usable in the product surface
- Unknown remains unknown — the system does not fill gaps with estimates
- overall_fallback remains clearly marked when evidence is insufficient

**FAIL if:**
- A life_score field appears anywhere in the output
- An exact probability is emitted without a validated model card
- A population_percentile is computed without a numeric baseline
- Unknown states are filled with default estimates
- Marketing copy implies statistical certainty or source-backed personal destiny prediction

**v1.0-rc status:** ✅ PASS — tests confirm no life_score and no unsupported exact probability. `extra="forbid"` on all schemas.

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

**v1.0-rc status:** ✅ PASS — Full traceability verified: forecast → snapshot → evidence → evaluation → scorecard.

## Contract Enforcement

The `PublicPriorIntegrationContract` schema (in `apps/api/src/alters_lab/schemas/public_prior_contract.py`) encodes these gates as machine-readable guards and disallowed behaviors. Any integration code must validate against this contract before allowing external reference context into the forecast path.

## Distribution and Commercial-Use Rule

The repository's MIT license covers the software and documentation in this repository. It does not grant rights to redistribute third-party raw data, processed source files, licensed codebooks, restricted-use datasets, or offline artifacts derived from those sources.

Before any commercial release:
- Keep raw data, processed data, and offline artifacts out of the public repo and product bundle
- Use neutral product language such as "optional reference context" rather than named dataset claims
- Keep citation and attribution in internal documentation or a dedicated compliance note, not as a marketing hook
- Confirm each external source's terms before distribution, hosted inference, resale, or bundling
