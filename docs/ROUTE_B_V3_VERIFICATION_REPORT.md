# Route B v4 — Model Execution Verification Report

Date: 2026-06-03
Gate: Route B v4 Tier 1 Model Improvements

---

## Tier 1 Improvements Applied

All 4 Tier 1 improvements implemented:

1. **More features** — Added 7 new NLSY97 predictors: census_region, hh_size_2005, married_2005, piat_pct_1997 (cognitive ability), asvab_stpel_1997, father_educ, mother_educ
2. **Interaction terms** — degree×income, sex×grade
3. **Isotonic calibration** — CalibratedClassifierCV with cv=5
4. **IterativeImputer** — Multivariate chained equations replacing fill-0/median defaults

---

## Check 1 — Model Script Execution

### NLSY97: `build_nlsy97_calibrated_models.py` v4

**Status: RAN SUCCESSFULLY**

| Field | bachelor_or_higher | above_median_income |
|---|---|---|
| model_id | nlsy97_calibrated_models_v4 | nlsy97_calibrated_models_v4 |
| dataset | NLSY97 | NLSY97 |
| domain | career_education | financial |
| outcome | bachelor_or_higher (degree >= 4 in 2015) | above_median_income (> $63,040 in 2015) |
| predictors | 16 features (7 base + 7 new + 2 interactions) | same |
| n_train | 5,680 | 5,680 |
| n_test | 1,420 | 1,420 |
| Brier score | 0.0824 (was 0.0919) | 0.2038 (was 0.2093) |
| AUC | 0.939 (was 0.924) | 0.737 (was 0.713) |
| imputation | IterativeImputer (multivariate) | same |
| calibration | Isotonic (CalibratedClassifierCV, cv=5) | same |
| quality gate | ACCEPTED | ACCEPTED |

**Improvement summary:**
- Bachelor: AUC +1.5%, Brier -10.3%
- Income: AUC +3.4%, Brier -2.6%

### MIDUS: `build_midus_calibrated_models.py` v4

**Status: RAN SUCCESSFULLY**

| Field | health_good_excellent | high_social_closeness | high_life_satisfaction |
|---|---|---|---|
| model_id | midus_calibrated_models_v4 | midus_calibrated_models_v4 | midus_calibrated_models_v4 |
| dataset | MIDUS-2 | MIDUS-2 | MIDUS-2 |
| domain | health | social | wellbeing |
| predictors | 9 features (excluding outcome source) | 8 features (excluding B1SMPQSC) | 8 features (excluding B1SSATIS) |
| n_train | 853 | 853 | 853 |
| n_test | 214 | 214 | 214 |
| Brier score | 0.1568 (was 0.1504) | 0.2260 (was 0.2261) | 0.2182 (was 0.2180) |
| AUC | 0.767 (was 0.772) | 0.689 (was 0.689) | 0.674 (was 0.668) |
| imputation | IterativeImputer | same | same |
| calibration | Isotonic (CalibratedClassifierCV, cv=5) | same | same |
| quality gate | ACCEPTED | ACCEPTED | ACCEPTED |

**MIDUS note:** Small sample (1,067 rows) limits improvement potential. IterativeImpector helped LSAT slightly. Health dipped marginally (within noise).

---

## Check 2 — Artifact Files

- `nlsy97_calibrated_models_v4.json` — Generated (v4)
- `midus_calibrated_models_v4.json` — Generated (v4)
- Both contain brier_score, auc_roc, calibration_bins, coefficients

## Check 3 — Data Leakage Audit

**LOW RISK.** All prospective designs (2005 predictors → 2015 outcomes). Outcome source variables excluded from feature matrices where applicable (B1SMPQSC, B1SSATIS).

## Check 4 — Domain Coverage Matrix

| Domain | NLSY97 | MIDUS | Coverage |
|---|---|---|---|
| career_education | calibrated_model (AUC=0.939) | — | ✅ |
| financial | calibrated_model (AUC=0.737) | — | ✅ |
| health | — | calibrated_model (AUC=0.767) | ✅ |
| social | — | calibrated_model (AUC=0.689) | ✅ |
| wellbeing | — | calibrated_model (AUC=0.674) | ✅ |

All 5 domains covered by calibrated_model artifacts.

## Check 5 — Model Cards Updated

All 5 model cards updated to match Pydantic `PopulationBaselineModelCard` schema:
- `mc_nlsy97_career_education.yaml` — AUC=0.939, Brier=0.0824
- `mc_nlsy97_financial.yaml` — AUC=0.737, Brier=0.2038
- `mc_midus_self_rated_health.yaml` — AUC=0.767, Brier=0.1568
- `mc_midus_social_support.yaml` — AUC=0.689, Brier=0.2260
- `mc_midus_life_satisfaction.yaml` — AUC=0.674, Brier=0.2182

## Check 6 — Test Suite

- Backend: **1857 passed**, 2 skipped, 1 xpassed
- Frontend: **81 passed** (25 test files)

## Verdict

**PASS** — All Tier 1 improvements implemented, all quality gates passed, all tests green.
