# Route B v3 — Time-Order / Leakage Audit

Date: 2026-06-03
Auditor: Claude Code verification gate

## Methodology

For each model, classify as cross-sectional or prospective based on predictor/outcome timing.
Flag any predictor that directly encodes the outcome.

---

## NLSY97 Models

### bachelor_or_higher (career_education)

- **Predictors (2005):** grade_2005, degree_2005, income_2005, sex_female, race_white, race_black, race_hispanic
- **Outcome (2015):** U0009400 — CV_HIGHEST_DEGREE_EVER 2015
- **Classification:** Prospective (10-year gap: 2005 → 2015)
- **Leakage risk:** LOW

**Analysis:** The outcome is degree attainment in 2015. The predictor `degree_2005` is the respondent's highest degree in 2005. These are temporally distinct measurements — someone with a bachelor's in 2005 will likely have one in 2015, but someone without one in 2005 may earn one by 2015. The predictor is not the same measurement as the outcome. No leakage.

**Note:** `degree_2005` is a strong predictor because degree attainment is highly stable. This is a feature of the domain, not leakage. The AUC of 0.924 reflects this strong temporal correlation.

### above_median_income (financial)

- **Predictors (2005):** grade_2005, degree_2005, income_2005, sex_female, race_white, race_black, race_hispanic
- **Outcome (2015):** U0008900 — CV_INCOME_FAMILY 2015
- **Classification:** Prospective (10-year gap: 2005 → 2015)
- **Leakage risk:** LOW

**Analysis:** `income_2005` predicts `income_2015`. These are from different survey rounds (S5412800 vs U0008900). Income is autocorrelated but not identical. No leakage.

---

## MIDUS Models — SCRIPT BROKEN, NO MODELS PRODUCED

The `build_midus_calibrated_models.py` script references 5 variable names that do not exist in the MIDUS-2 SPSS file:

| Script variable | Actual MIDUS-2 variable | Status |
|---|---|---|
| B1SCONDP | B1SCONST (Perceived Constraints) | WRONG NAME |
| B1SCALL | Does not exist | MISSING |
| B1SCSAT | Does not exist | MISSING |
| B1SA52A | B1SA52 ("Needed med care, couldn't get it") | WRONG NAME + WRONG MEANING |
| B1SA40A | B1SA40 ("Weight 1 year ago") | WRONG NAME + WRONG MEANING |

**Impact:**
- `high_social_support` outcome produced 0% positive rate (all imputed to 0) — model training crashed with "only one class" error
- Sleep quality and physical activity features are actually medical access and weight variables
- The script has never successfully run against real MIDUS-2 data

**Cannot audit leakage for MIDUS models because no models were produced.**

---

## Summary

| Model | Dataset | Type | Leakage Risk | Status |
|---|---|---|---|---|
| bachelor_or_higher | NLSY97 | Prospective | LOW | ACCEPTED |
| above_median_income | NLSY97 | Prospective | LOW | ACCEPTED |
| health_good_excellent | MIDUS | N/A | N/A | BROKEN |
| high_social_support | MIDUS | N/A | N/A | BROKEN |
| high_life_satisfaction | MIDUS | N/A | N/A | BROKEN |

**Verdict:** NLSY97 models pass leakage audit. MIDUS models cannot be audited because the script is broken.
