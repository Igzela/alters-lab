# Route B v4 — Domain Coverage Matrix

Date: 2026-06-03
Status: Post Tier 1 improvements

## Coverage Matrix

| Domain | Best Artifact Class | Artifact ID | Model Card ID | Metrics | Approval Level |
|---|---|---|---|---|---|
| career_education | calibrated_model | nlsy97_calibrated_models_v4 | mc_nlsy97_career_education | AUC=0.939, Brier=0.0824 | route_b_approved |
| financial | calibrated_model | nlsy97_calibrated_models_v4 | mc_nlsy97_financial | AUC=0.737, Brier=0.2038 | route_b_approved |
| health | calibrated_model | midus_calibrated_models_v4 | mc_midus_self_rated_health | AUC=0.767, Brier=0.1568 | route_b_approved |
| social | calibrated_model | midus_calibrated_models_v4 | mc_midus_social_support | AUC=0.689, Brier=0.2260 | route_b_approved |
| wellbeing | calibrated_model | midus_calibrated_models_v4 | mc_midus_life_satisfaction | AUC=0.674, Brier=0.2182 | route_b_approved |

## Tier 1 Improvements (v4)

### NLSY97 (career_education, financial)
- **7 new features**: census_region, hh_size_2005, married_2005, piat_pct_1997, asvab_stpel_1997, father_educ, mother_educ
- **2 interaction terms**: degree×income, sex×grade
- **Isotonic calibration**: CalibratedClassifierCV with cv=5
- **IterativeImputer**: Multivariate chained equations replacing fill-0/median
- Total: 16 features (was 7)
- Bachelor AUC: 0.924 → 0.939, Brier: 0.0919 → 0.0824
- Income AUC: 0.713 → 0.737, Brier: 0.2093 → 0.2038

### MIDUS (health, social, wellbeing)
- **Isotonic calibration**: CalibratedClassifierCV with cv=5
- **IterativeImputer**: Multivariate chained equations replacing fixed defaults
- Health AUC: 0.772 → 0.767 (stable), LSAT AUC: 0.668 → 0.674 (improved)

## Summary

**All 5 domains have calibrated_model artifacts with route_b_approved status.**

- 2 domains from NLSY97 (career_education, financial) — 16 features, 7,100 rows
- 3 domains from MIDUS-2 (health, social, wellbeing) — 8-9 features, 1,067 rows
- All pass quality gate: AUC ≥ 0.6, Brier ≤ 0.25
- All use isotonic calibration + IterativeImputer

## Relationship Domain

The `relationship` domain uses a literature-based contextual prior (`pa_lit_relationship`) with `lab_only` approval. The `social` domain from MIDUS covers social closeness/integration, which is a proxy for relationship quality. No dedicated relationship outcome dataset is available.
