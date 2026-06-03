# NLSY97 Calibrated Predictive Models v3

## Summary

Logistic regression models trained on NLSY97 longitudinal data, upgrading from descriptive baselines (v2) to calibrated predictive models. Uses 2005 round features (age 25-29) to predict 2015 round outcomes (age 31-35).

## Purpose

NLSY97 v2 provided descriptive population baselines -- aggregate distributions from a single cross-section. v3 adds predictive calibration: models that estimate the probability of specific outcomes given baseline characteristics. This is the minimum requirement for Route B approval as numeric priors.

## Data

### Source

- **Dataset**: National Longitudinal Survey of Youth 1997 (NLSY97)
- **Feature round**: 2005 (Round 9), respondents aged 25-29 (born 1980-84)
- **Outcome round**: 2015 (Round 17), respondents aged 31-35
- **Linking variable**: Respondent ID (unique panel identifier)
- **Sample**: 50,000 rows from 8.1GB CSV (89,814 total respondents)

### Longitudinal Design

| Round | Year | Age | Role |
|-------|------|-----|------|
| 9 | 2005 | 25-29 | Feature baseline (education, sex, race/ethnicity) |
| 17 | 2015 | 31-35 | Outcome measurement (degree attainment, income) |

This 10-year follow-up captures early-career trajectories. Outcomes at age 31-35 reflect completed education and established income patterns, not transient early-20s states.

## Outcomes

### bachelor_or_higher (binary)

- **Definition**: Respondent holds a bachelor's degree or higher by 2015
- **Source variable**: Highest Degree Ever Received (2015 round)
- **Coding**: 1 = bachelor's, master's, doctorate, or professional degree; 0 = otherwise
- **Expected prevalence**: ~30-35% (NLSY97 cohort, based on 2005 baseline of 12.1% bachelor's plus subsequent attainment)

### above_median_income (binary)

- **Definition**: Total family income above cohort median by 2015
- **Source variable**: Total Family Income (2015 round)
- **Coding**: 1 = income above 2015 cohort median; 0 = at or below
- **Median estimation**: Computed from 2015 round, not imputed from 2005

## Features

All features measured in the 2005 round (baseline).

| Feature | Variable Code | Type | Missingness | Notes |
|---------|--------------|------|-------------|-------|
| Highest Degree (2005) | S5413300 | Ordinal (0-7) | 18.56% | None through Professional degree |
| Highest Grade Completed (2005) | S5412600 | Continuous (0-20) | 19.07% | Years of schooling |
| Sex | R0536300 | Binary (1,2) | 0% | 1=Male, 2=Female |
| Race/Ethnicity | R1482600 | Categorical (1-5) | 0% | 1=Hispanic, 2=Black, 3=Non-Black/Non-Hispanic |

### Feature Engineering

- **Sex**: Binary indicator (0=Male, 1=Female)
- **Race/Ethnicity**: One-hot encoded (4 dummies: Hispanic, Black, Non-Black/Non-Hispanic white, Other)
- **Highest Degree**: Ordinal treated as continuous for logistic regression (sensitivity analysis with dummy encoding also reported)
- **Missingness handling**: Listwise deletion for model training (19-32% across education/income variables); multiple imputation explored as robustness check

## Model Specification

### Family

Logistic regression (generalized linear model with logit link).

Chosen for:
- Interpretability (coefficient = log-odds ratio)
- Calibrated probabilities without post-hoc adjustment
- Low data requirement relative to tree-based methods
- Standard reference model for social science prediction

### Training Protocol

- **Split**: 80% training, 20% holdout (stratified by outcome)
- **Cross-validation**: 5-fold CV on training set for hyperparameter-free model selection
- **Validation**: Holdout set metrics reported as primary; CV metrics as secondary
- **No regularization** in baseline models (vanilla logistic regression); elastic net variants documented separately

### Model ID Convention

```
nlsy97_{outcome}_{feature_set}_logistic_regression
```

Examples:
- `nlsy97_bachelor_or_higher_2005_baseline_logistic_regression`
- `nlsy97_above_median_income_2005_baseline_logistic_regression`

## Calibration Metrics

### bachelor_or_higher

| Metric | CV (5-fold) | Holdout (20%) | Interpretation |
|--------|-------------|---------------|----------------|
| Brier Score | [TBD] | [TBD] | <0.25 reasonable for binary outcome |
| AUC | [TBD] | [TBD] | >0.7 acceptable, >0.8 good |
| Calibration Slope | [TBD] | [TBD] | 1.0 = perfect; <1 = overfit |
| Calibration Intercept | [TBD] | [TBD] | 0.0 = perfect |
| Prevalence (outcome rate) | [TBD] | [TBD] | Base rate in sample |

### above_median_income

| Metric | CV (5-fold) | Holdout (20%) | Interpretation |
|--------|-------------|---------------|----------------|
| Brier Score | [TBD] | [TBD] | <0.25 reasonable |
| AUC | [TBD] | [TBD] | >0.7 acceptable |
| Calibration Slope | [TBD] | [TBD] | 1.0 = perfect |
| Calibration Intercept | [TBD] | [TBD] | 0.0 = perfect |
| Prevalence (outcome rate) | [TBD] | [TBD] | 50% by construction (median split) |

### Calibration Curve

Plots of predicted probability vs. observed frequency, binning predictions into deciles. Both models will include calibration curve data (predicted mean per bin vs. observed proportion per bin) as a JSON artifact for frontend visualization.

## Expected Model Behavior

### bachelor_or_higher

Strongest predictors (based on 2005 baseline):
- 2005 degree attainment (highest degree held at age 25-29 is the strongest signal)
- 2005 grade completed (years of schooling)
- Race/ethnicity (historical differences in degree attainment)
- Sex (historical differences, narrowing in younger cohorts)

Expected AUC: 0.70-0.80. Education at 25-29 is a strong but not perfect predictor of eventual degree completion -- some respondents complete bachelor's degrees in their late 20s and early 30s.

### above_median_income

Strongest predictors (expected):
- 2005 degree attainment (education-income relationship)
- Sex (gender wage gap persists in this cohort)
- Race/ethnicity (income disparities)
- 2005 family income (proxy for household economic context)

Expected AUC: 0.60-0.70. Income at 31-35 is noisier than degree attainment -- influenced by occupation, geography, partner income, economic conditions, and career trajectories not captured by baseline demographics alone.

## Limitations

### Cohort Specificity

- **Population**: Born 1980-84, US residents
- **Temporal context**: Feature baseline from 2005 (pre-Great Recession), outcome from 2015 (post-recovery)
- **Transfer risk**: HIGH. Modern cohorts (born 1995+) face different education costs, labor markets, and economic conditions. These priors should not be applied to users outside the 1980-84 birth cohort without explicit acknowledgment.

### Variable Definitions

- **Family income**: Household-level, not personal earnings. A respondent with high personal income but low family income (or vice versa) may be misclassified.
- **Income timing**: 2015 income is a single-year snapshot, not annualized or career-averaged.
- **Education coding**: Highest degree ever received -- does not distinguish between degree completion timing (some may have completed bachelor's between 2005-2015).

### Missingness

- Education features: 18-19% missing (survey non-response)
- Income outcomes: ~32% missing in 2005 round; 2015 round missingness TBD
- Listwise deletion reduces effective sample size; results may not generalize to non-respondents

### Methodological

- **Logistic regression**: Linear decision boundary in log-odds space; may miss non-linear interactions
- **No regularization**: Baseline models use vanilla logistic regression; overfitting risk in small samples
- **Single split**: Results depend on random seed; 5-fold CV mitigates but does not eliminate this

## Route B Approval Criteria

These models are candidates for Route B approval as `calibrated_model` artifacts. All criteria must be satisfied:

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Actual data used (not literature-only) | [ ] | NLSY97 2005+2015 rounds |
| Variable codes confirmed in raw data | [ ] | S5413300, S5412600, R0536300, R1482600 |
| Feature-outcome linkage (longitudinal) | [ ] | 2005 features -> 2015 outcomes via Respondent ID |
| Model trained with documented protocol | [ ] | Logistic regression, 80/20 split, 5-fold CV |
| Calibration metrics reported | [ ] | Brier, AUC, calibration slope/intercept |
| Calibration curve available | [ ] | Decile-binned predicted vs. observed |
| Model card completed | [ ] | See template fields below |
| Transfer risk documented | [ ] | HIGH -- cohort-specific, see limitations |
| Safety checks passed | [ ] | No raw data, no individual predictions |

### Approval Gate

Models meet Route B approval when:
1. All metrics are computed and documented (TBD values filled)
2. Calibration slope is within [0.7, 1.3] (no severe miscalibration)
3. AUC exceeds 0.65 for both outcomes
4. Brier score is below 0.25 for both outcomes
5. Model card is complete with all required fields

## Safety Confirmations

- **No raw data committed**: Only aggregate statistics, model coefficients, and evaluation metrics stored in repository
- **No individual predictions**: Models emit population-level probability distributions, not individual-level risk scores
- **No life_score integration**: These priors inform branch forecasts; they do not compute or modify life scores
- **No PII in outputs**: Respondent IDs used for longitudinal linking during training only; not stored in model artifacts
- **Audit trail**: Model cards document training data, protocol, and metrics for reproducibility

## Artifact Locations

- **Model coefficients**: `labs/population_baseline/artifacts/nlsy97_*_coefficients.json` (after training)
- **Evaluation metrics**: `labs/population_baseline/artifacts/nlsy97_*_metrics.json` (after training)
- **Calibration curves**: `labs/population_baseline/artifacts/nlsy97_*_calibration.json` (after training)
- **Model cards**: `labs/population_baseline/artifacts/nlsy97_*_model_card.json` (after training)

## Model Card Fields

Following `model_card_template.md`, each model card includes:

```json
{
  "model_id": "nlsy97_bachelor_or_higher_2005_baseline_logistic_regression",
  "source_dataset": "nlsy97",
  "outcome": "bachelor_or_higher",
  "features": ["highest_degree_2005", "highest_grade_2005", "sex", "race_ethnicity"],
  "model_family": "logistic_regression",
  "training_status": "not_trained",
  "training_date": null,
  "training_sample_size": null,
  "split": "80/20 stratified",
  "cv_folds": 5,
  "metrics": {
    "brier_score": null,
    "auc": null,
    "calibration_slope": null,
    "calibration_intercept": null
  },
  "transfer_risk": "high",
  "transfer_rationale": "Cohort-specific (born 1980-84), US-only, 2005 baseline, family income not personal",
  "approved_for_route_b": false,
  "approval_conditions": "Requires computed metrics meeting threshold criteria"
}
```

## Next Steps

1. **Training**: Run logistic regression on linked 2005->2015 NLSY97 panel
2. **Evaluation**: Compute Brier, AUC, calibration metrics on holdout set
3. **Calibration curves**: Generate decile-binned predicted vs. observed data
4. **Model cards**: Complete model card JSON for both outcomes
5. **Approval review**: Submit for Route B approval gate
6. **Elastic net variants**: Train regularized variants as robustness check
7. **Sensitivity analysis**: Test with dummy-encoded education (vs. ordinal)
