# Route B v3 — Domain Coverage Matrix

Date: 2026-06-03
Status: Verification gate

## Coverage Matrix

| Domain | Best Artifact Class | Approved Artifact ID | Model Card ID | Metrics Available | Approval Level | Blocker |
|---|---|---|---|---|---|---|
| career_education | calibrated_model | pa_nlsy97_career_education | mc_nlsy97_career_education | Brier=0.0919, AUC=0.924, 10 calibration bins | route_b_approved* | None — model trained and accepted |
| financial | calibrated_model | pa_nlsy97_financial | mc_nlsy97_financial | Brier=0.2093, AUC=0.713, 10 calibration bins | route_b_approved* | None — model trained and accepted |
| health | data_backed_baseline | pa_midus_self_rated_health | mc_midus_self_rated_health | All null | route_b_approved | MIDUS calibrated script broken (wrong variable names) |
| relationship | contextual_prior | pa_lit_relationship | mc_lit_relationship | All null | lab_only | No data-backed artifact exists; literature prior only |
| subjective_wellbeing | data_backed_baseline | pa_midus_life_satisfaction | mc_midus_life_satisfaction | All null | route_b_approved | MIDUS calibrated script broken (wrong variable names) |

## Notes

### career_education and financial (NLSY97)

Both domains now have **actual calibrated models** trained on NLSY97 data (7,100 usable rows from 2005→2015 prospective design). Model artifacts written to `labs/population_baseline/artifacts/nlsy97_calibrated_models_v3.json`.

However, the model cards and artifacts in `alters/product/` have NOT been updated with these metrics. The existing `mc_nlsy97_career_education.yaml` and `mc_nlsy97_financial.yaml` still have all-null calibration_metrics and `artifact_class: data_backed_baseline`.

**To promote to calibrated_model status**, the product artifacts need to be regenerated from the script output.

### health and subjective_wellbeing (MIDUS)

The MIDUS calibrated model script (`build_midus_calibrated_models.py`) references 5 variables that don't exist in the MIDUS-2 SPSS file. The script crashes on the `high_social_support` model (0% positive rate). The other two models (health, life_satisfaction) would also use incorrect feature variables if the script were fixed.

**Blocker:** Script must be fixed with correct MIDUS-2 variable names before calibrated models can be produced.

### relationship

No data-backed artifact exists. Only a literature-based contextual prior (`pa_lit_relationship`) with `lab_only` approval. This domain has no population data backing.

**Blocker:** Needs a dataset with relationship outcome variables (e.g., NLSY97 marriage/cohabitation status, MIDUS relationship quality scales).

## Summary

- **2/5 domains** have calibrated models (career_education, financial) — but product artifacts not yet updated
- **2/5 domains** have data-backed baselines but no calibrated models (health, subjective_wellbeing) — MIDUS script broken
- **1/5 domains** has only a contextual prior (relationship) — no data source

**Claim "all 5 domains have calibrated_model" is FALSE.**
