# Route B v3 — Promotion Audit

Date: 2026-06-03
Auditor: Automated promotion gate

## Promotion Gate Rules

A model earns `calibrated_model` + `route_b_approved` only if ALL of:
1. AUC improves over baseline/null model
2. Brier score improves over baseline
3. Calibration bins are present (or model is well-calibrated by design)
4. Leakage audit is low/medium, not high
5. n_train/n_test are documented

Models that pass quality gate (AUC ≥ 0.6, Brier ≤ 0.25) but do NOT show meaningful improvement are demoted to `data_backed_baseline` + `route_b_approved`. They remain useful as descriptive baselines but should not be presented as strong predictive models.

## Promotion Decisions

### NLSY97 — ACCEPTED as calibrated_model

| Model | AUC | Brier | AUC Δ | Brier Δ | Decision |
|---|---|---|---|---|---|
| bachelor_or_higher | 0.939 | 0.0824 | +1.6% | -10.3% | ✅ calibrated_model + route_b_approved |
| above_median_income | 0.737 | 0.2038 | +3.4% | -2.6% | ✅ calibrated_model + route_b_approved |

**Rationale:** Both models show clear improvement over v3 baseline. Bachelor model has excellent discrimination (AUC=0.939). Income model has good discrimination (AUC=0.737). Both benefit from 16 features (was 7), isotonic calibration, and IterativeImputer.

**Leakage audit:** LOW. Prospective design (2005→2015). No outcome variables in feature matrix.

### MIDUS — DEMOTED to data_backed_baseline

| Model | AUC | Brier | AUC Δ | Brier Δ | Decision |
|---|---|---|---|---|---|
| health_good_excellent | 0.767 | 0.1568 | -0.6% | +4.2% | ⚠️ data_backed_baseline + route_b_approved |
| high_social_closeness | 0.689 | 0.2260 | 0.0% | 0.0% | ⚠️ data_backed_baseline + route_b_approved |
| high_life_satisfaction | 0.674 | 0.2182 | +0.9% | +0.1% | ⚠️ data_backed_baseline + route_b_approved |

**Rationale:** MIDUS models show negligible or negative improvement after Tier 1 enhancements. The effective sample size (1,067 rows) is too small for the additional features and interactions to help. The models pass the quality gate (AUC ≥ 0.6, Brier ≤ 0.25) and are useful as descriptive baselines, but should not be presented as strong calibrated predictions.

**Key issues:**
- Health model: AUC actually decreased (0.772→0.767), Brier worsened (0.1504→0.1568)
- Social model: No change at all (AUC=0.689, Brier=0.226)
- LSAT model: Marginal AUC gain (+0.006), no Brier improvement
- All models: n_test=214 is too small for reliable calibration assessment

**What would change this decision:**
- Larger MIDUS sample (MIDUS 1+2 combined, ~7,000 rows)
- Better outcome variables (multi-item scales instead of single questions)
- Relaxing sentinel filtering to keep more rows

## Final 5-Domain Strength Matrix

| Domain | Source | artifact_class | approval_level | strength_level | AUC | Brier |
|---|---|---|---|---|---|---|
| career_education | NLSY97 | calibrated_model | route_b_approved | strong_calibrated | 0.939 | 0.082 |
| financial | NLSY97 | calibrated_model | route_b_approved | strong_calibrated | 0.737 | 0.204 |
| health | MIDUS | data_backed_baseline | route_b_approved | data_backed | 0.767 | 0.157 |
| social | MIDUS | data_backed_baseline | route_b_approved | data_backed | 0.689 | 0.226 |
| wellbeing | MIDUS | data_backed_baseline | route_b_approved | data_backed | 0.674 | 0.218 |

## Artifact Class Hierarchy

```
calibrated_model + route_b_approved  →  "strong_calibrated"  (AUC/Brier improved, validated)
data_backed_baseline + route_b_approved  →  "data_backed"     (passes quality gate, descriptive)
contextual_prior + lab_only  →  "contextual"                   (literature-based, no data)
none  →  "none"                                                 (no prior available)
```

## Forecast Ranking

When selecting artifacts for domain predictions:
1. `strong_calibrated` — preferred, confidence = high
2. `data_backed` — acceptable, confidence = medium
3. `contextual` — fallback, confidence = low
4. `none` — no prior available

## Safety Confirmations

- No life_score emitted
- No fake exact probability
- No raw data committed
- All models are population baselines, not individual predictions
