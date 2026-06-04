# Route B — Domain Strength Matrix

Date: 2026-06-03
Status: Post promotion audit

## Strength Levels

| Level | Label | Description | Confidence |
|---|---|---|---|
| `strong_calibrated` | Strong Calibrated Model | Logistic regression with validated calibration metrics, AUC/Brier improvement confirmed | high |
| `data_backed` | Data-Backed Descriptive Baseline | Passes quality gate (AUC≥0.6, Brier≤0.25) but no meaningful improvement over baseline | medium |
| `contextual` | Contextual Literature Prior | Literature-based estimate, no dataset-backed model | low |
| `none` | No Prior | No artifact available for this domain | low |

## Current Matrix

| Domain | strength_level | Source | artifact_class | Model Card | AUC | Brier | Transfer Risk |
|---|---|---|---|---|---|---|---|
| career_education | **strong_calibrated** | NLSY97 | calibrated_model | mc_nlsy97_career_education | 0.939 | 0.082 | high |
| financial | **strong_calibrated** | NLSY97 | calibrated_model | mc_nlsy97_financial | 0.737 | 0.204 | high |
| health | **data_backed** | MIDUS-2 | data_backed_baseline | mc_midus_self_rated_health | 0.767 | 0.157 | medium |
| relationship | **contextual** | Literature | contextual_prior | mc_lit_relationship | — | — | high |
| subjective_wellbeing | **data_backed** | MIDUS-2 | data_backed_baseline | mc_midus_life_satisfaction | 0.674 | 0.218 | medium |

## Coverage Summary

- **2/5 domains** have strong calibrated models (career_education, financial)
- **2/5 domains** have data-backed descriptive baselines (health, subjective_wellbeing)
- **1/5 domain** has a contextual literature prior (relationship)
- **0/5 domains** have no prior at all

## Display Rules

### Branch Forecast UI
- `strong_calibrated` → "Strong Calibrated Public Model" (green badge)
- `data_backed` → "Data-Backed Descriptive Baseline" (amber badge)
- `contextual` → "Contextual Literature Prior" (gray badge)
- `none` → "No Route B Prior" (gray badge)

### Public Priors UI
- Coverage matrix shows strength_level column
- Model cards show strength level in approval panel
- Artifacts show strength badge next to artifact class

## What Each Level Means for Users

### strong_calibrated
The model has been trained on real population data, validated with proper train/test split, and shows genuine predictive improvement. The calibration metrics (Brier score, AUC) are trustworthy indicators of model quality. Use these priors with moderate confidence.

### data_backed
The model is trained on real data and passes basic quality checks, but doesn't predict outcomes much better than a simple baseline. Treat these as descriptive statistics ("this is what the population looks like") rather than predictive models ("this is what will happen to you").

### contextual
Based on literature review or expert opinion, not a trained model. Use these as rough directional guidance only.

## Promotion Gate Criteria

To promote from `data_backed` to `strong_calibrated`, a model must show:
- AUC improvement over null/baseline model
- Brier score improvement over null/baseline model
- Sufficient sample size (n_test ≥ 500 recommended)
- Low/medium leakage risk
- Calibration bins present and reasonable
