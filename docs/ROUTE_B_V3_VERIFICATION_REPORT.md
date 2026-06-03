# Route B v3 — Model Execution Verification Report

Date: 2026-06-03
Gate: Route B v3 Model Execution Verification

---

## Check 1 — Model Script Execution

### NLSY97: `build_nlsy97_calibrated_models.py`

**Status: RAN SUCCESSFULLY**

| Field | bachelor_or_higher | above_median_income |
|---|---|---|
| model_id | nlsy97_calibrated_models_v3 | nlsy97_calibrated_models_v3 |
| dataset | NLSY97 | NLSY97 |
| domain | career_education | financial |
| outcome | bachelor_or_higher (degree >= 4 in 2015) | above_median_income (> $63,040 in 2015) |
| predictors | grade_2005, degree_2005, income_2005, sex_female, race_white, race_black, race_hispanic | same |
| n_train | 5,680 | 5,680 |
| n_test | 1,420 | 1,420 |
| class balance (train) | 28.8% positive | 42.4% positive |
| class balance (test) | 26.4% positive | 42.0% positive |
| Brier score | 0.0919 | 0.2093 |
| AUC | 0.924 | 0.713 |
| calibration bins | 10 bins | 10 bins |
| missingness handling | Impute: grade→12, degree→2, income→0, sex→male, race→other | same |
| train/test split | 80/20, random_state=42 | same |
| target timing | 2015 (10 years after predictors) | same |
| leakage risk | LOW | LOW |
| quality gate | ACCEPTED (AUC≥0.6, Brier≤0.25) | ACCEPTED |

**Calibration quality (bachelor_or_higher):** Well-calibrated in high-probability bins (pred 0.712 → actual 0.683; pred 0.954 → actual 0.979). Low-probability bins show some overconfidence (pred 0.085 → actual 0.035).

**Calibration quality (above_median_income):** Moderate calibration. Mid-range bins show deviation (pred 0.338 → actual 0.458). Acceptable for a 7-feature logistic regression.

### MIDUS: `build_midus_calibrated_models.py`

**Status: SCRIPT BROKEN — CRASHED**

The script references 5 variable names that do not exist in the MIDUS-2 SPSS file:

| Script name | Actual MIDUS-2 variable | Issue |
|---|---|---|
| B1SCONDP | B1SCONST (Perceived Constraints) | Wrong suffix |
| B1SCALL | Does not exist | Entirely missing |
| B1SCSAT | Does not exist | Entirely missing |
| B1SA52A | B1SA52 | Wrong suffix; label is "Needed med care" not sleep quality |
| B1SA40A | B1SA40 | Wrong suffix; label is "Weight 1 year ago" not physical activity |

**Crash:** `high_social_support` had 0% positive rate (all values imputed to 0 since B1SCALL doesn't exist), causing sklearn to throw "only one class" error.

**No MIDUS calibrated models were produced.**

---

## Check 2 — Artifact File Audit

### Model Cards (`alters/product/model_cards/`)

| Model Card | artifact_class | approval_level | calibration_metrics | Verdict |
|---|---|---|---|---|
| mc_nlsy97_career_education | data_backed_baseline | route_b_approved | ALL NULL | Should be upgraded to calibrated_model |
| mc_nlsy97_financial | data_backed_baseline | route_b_approved | ALL NULL | Should be upgraded to calibrated_model |
| mc_midus_self_rated_health | data_backed_baseline | route_b_approved | ALL NULL | Correct (no calibrated model exists) |
| mc_midus_chronic_conditions | data_backed_baseline | route_b_approved | ALL NULL | Correct |
| mc_midus_social_support | data_backed_baseline | route_b_approved | ALL NULL | Correct |
| mc_midus_life_satisfaction | data_backed_baseline | route_b_approved | ALL NULL | Correct |
| mc_midus_perceived_control | data_backed_baseline | route_b_approved | ALL NULL | Correct |
| mc_lit_career_financial | contextual_prior | lab_only | ALL NULL | Correct (literature prior) |
| mc_lit_health | contextual_prior | lab_only | ALL NULL | Correct |
| mc_lit_relationship | contextual_prior | lab_only | ALL NULL | Correct |
| mc_lit_subjective_wellbeing | contextual_prior | lab_only | ALL NULL | Correct |

**Critical: Zero model cards have populated calibration_metrics.** The NLSY97 calibrated models were trained but never propagated to product model cards.

### Artifacts (`alters/product/population_prior_artifacts/`)

| Artifact | artifact_class | actual_data_used | value_labels_confirmed | missingness_reviewed |
|---|---|---|---|---|
| pa_nlsy97_career_education | data_backed_baseline | true | true | true |
| pa_nlsy97_financial | data_backed_baseline | true | true | true |
| pa_midus_self_rated_health | data_backed_baseline | true | true | true |
| pa_midus_chronic_conditions | data_backed_baseline | true | true | true |
| pa_midus_social_support | data_backed_baseline | true | true | true |
| pa_midus_life_satisfaction | data_backed_baseline | true | true | true |
| pa_midus_perceived_control | data_backed_baseline | true | true | true |
| pa_lit_* (5 artifacts) | contextual_prior | false | false | false |

**No artifact has artifact_class=calibrated_model.** All data-backed artifacts correctly have guardrail flags set.

---

## Check 3 — Time-Order / Leakage Audit

**See: `docs/ROUTE_B_V3_LEAKAGE_AUDIT.md`**

| Model | Type | Leakage Risk |
|---|---|---|
| bachelor_or_higher | Prospective (2005→2015) | LOW |
| above_median_income | Prospective (2005→2015) | LOW |
| health_good_excellent | N/A (script broken) | N/A |
| high_social_support | N/A (script broken) | N/A |
| high_life_satisfaction | N/A (script broken) | N/A |

No predictor directly encodes the outcome. `degree_2005` predicting `degree_2015` is temporal autocorrelation, not leakage.

---

## Check 4 — Domain Coverage Matrix

**See: `docs/ROUTE_B_V3_MODEL_COVERAGE.md`**

| Domain | Best Class | Has Calibrated Model? | Blocker |
|---|---|---|---|
| career_education | calibrated_model | YES (NLSY97) | Product artifacts not updated |
| financial | calibrated_model | YES (NLSY97) | Product artifacts not updated |
| health | data_backed_baseline | NO | MIDUS script broken |
| relationship | contextual_prior | NO | No data source |
| subjective_wellbeing | data_backed_baseline | NO | MIDUS script broken |

**Claim "all 5 domains have calibrated_model" is FALSE.**

---

## Check 5 — Forecast Behavior

### Tests (106 pass)

| Test | Assertion | Status |
|---|---|---|
| test_forecast_prefers_calibrated_model | priority calibrated_model > data_backed_baseline | PASS |
| test_approval_hierarchy_order | calibrated(3) > data_backed(2) > contextual(1) | PASS |
| test_calibrated_model_requires_brier_or_auc | calibrated_model + route_b_approved needs metrics | PASS |
| test_calibrated_artifact_all_checks_must_pass | actual_data + value_labels + missingness required | PASS |
| test_no_life_score | No life_score in forecast result | PASS |
| test_no_life_score_in_domain_predictions | No life_score in domain predictions | PASS |
| test_no_life_score_in_prior_artifact | No life_score in artifacts | PASS |
| test_no_life_score_in_model_card | No life_score in model cards | PASS |
| test_snapshot_no_life_score | No life_score in snapshots | PASS |

### Bug Found & Fixed: `best_artifact_class` never assigned

In `services/branch_forecast.py`, `best_artifact_class` was computed at line 120-122 but **not passed** to the `BranchForecastResult` constructor at line 247-264. The field defaulted to `"none"` in all API responses.

**Fix applied:** Added `best_artifact_class=best_artifact_class` to the `BranchForecastResult` constructor. All 1857 backend tests pass after fix.

### Calibration Metrics Aggregation

The `setdefault` pattern at lines 162-171 takes metrics from whichever artifact appears first in the iteration order, not explicitly from the highest-priority artifact. This works correctly when calibrated_model artifacts exist (they'd be iterated first if the list is sorted), but the code comment is misleading.

---

## Check 6 — Frontend Behavior

### Public Priors Page (`PublicPriors.tsx`)

- Coverage tab: displays domain matrix with artifact_class badges ✓
- Artifacts tab: shows actual_data_used, value_labels_confirmed, missingness_reviewed ✓
- Model Cards tab: shows calibration metrics when non-null, "Primary Validation" badge for calibrated_model ✓
- **Issue:** Since no model cards have populated metrics, the metrics section always shows empty/null placeholders

### Branch Forecast Page (`BranchForecast.tsx`)

- Route B section: displays artifact_class badge (Calibrated/Descriptive/Contextual) ✓
- Shows calibration metrics (Brier, Slope, AUC, R²) when available ✓
- Warning when route B not fully approved ✓
- **Issue:** `best_artifact_class` always "none" due to backend bug

### Verdict

Frontend code correctly handles calibrated_model display when metrics exist. The problem is that no metrics exist in the product artifacts.

---

## Check 7 — Safety

### Test Suite

| Suite | Result |
|---|---|
| Backend (1857 tests) | 1857 passed, 2 skipped, 1 xpassed |
| Frontend (81 tests, 25 files) | 81 passed |
| Frontend build | ✓ built in 3.16s |

### Safety Confirmations

| Check | Status |
|---|---|
| No raw data staged/committed | ✓ git status clean |
| No processed individual-level rows | ✓ aggregate statistics only |
| No active YAML/rubric drift | ✓ git status clean |
| No provider/LLM call with raw data | ✓ no provider integration |
| No life_score | ✓ guarded by extra="forbid" + 8 test assertions |
| No fake probability | ✓ no exact probability without calibration |
| No exact personal probability | ✓ Route B produces direction only |

---

## Summary of Findings

### What Works

1. NLSY97 calibrated model scripts run successfully, producing 2 accepted models
2. Schema guardrails are correct and well-tested (106 Route B tests pass)
3. Forecast hierarchy logic (calibrated > data_backed > contextual) is implemented
4. life_score is cleanly absent with multiple guard layers
5. Frontend correctly handles artifact class display
6. All 1857 backend + 81 frontend tests pass
7. Frontend builds clean
8. **`best_artifact_class` bug fixed** — now correctly assigned in BranchForecastResult

### What's Broken

1. **MIDUS calibrated model script is fundamentally broken** — 5 wrong variable names, never produced a model
2. **Product model cards have all-null calibration_metrics** — NLSY97 trained models never propagated
3. **No calibrated_model artifacts exist** in `alters/product/` — all are data_backed_baseline

### Required Actions

1. **DONE:** Fixed `best_artifact_class` assignment in BranchForecastResult constructor
2. Fix `build_midus_calibrated_models.py` with correct MIDUS-2 variable names
3. Regenerate product model cards and artifacts from NLSY97 script output
4. Add test asserting `best_artifact_class` is populated when calibrated artifacts exist
5. Add snapshot test asserting `artifact_class` preservation on domain predictions

### Metrics Table (NLSY97 — only models that actually ran)

| Model | Brier | AUC | n_train | n_test | Status |
|---|---|---|---|---|---|
| bachelor_or_higher | 0.0919 | 0.924 | 5,680 | 1,420 | accepted |
| above_median_income | 0.2093 | 0.713 | 5,680 | 1,420 | accepted |
| health_good_excellent | — | — | — | — | BROKEN |
| high_social_support | — | — | — | — | BROKEN |
| high_life_satisfaction | — | — | — | — | BROKEN |

### Domain Coverage (Ground Truth)

| Domain | Actual Best Class | Calibrated? | Product Artifact Updated? |
|---|---|---|---|
| career_education | calibrated_model | YES | NO |
| financial | calibrated_model | YES | NO |
| health | data_backed_baseline | NO | N/A |
| relationship | contextual_prior | NO | N/A |
| subjective_wellbeing | data_backed_baseline | NO | N/A |
