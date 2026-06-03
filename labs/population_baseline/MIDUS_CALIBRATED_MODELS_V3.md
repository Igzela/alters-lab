# MIDUS Calibrated Predictive Models v3

## Summary

Logistic regression models trained on MIDUS 2 cross-sectional data, upgrading from descriptive baselines (v2) to calibrated predictive models. Uses a single wave of adult midlife respondents to predict binary outcome thresholds for health, social support, and life satisfaction.

## Purpose

MIDUS v2 provided descriptive population baselines -- aggregate distributions from three cross-sectional waves. v3 adds predictive calibration: models that estimate the probability of specific outcomes given baseline characteristics. This is the minimum requirement for Route B approval as numeric priors. Unlike NLSY97 (which has longitudinal feature-to-outcome linkage), MIDUS v3 models are cross-sectional classifiers trained on MIDUS 2 alone, with no longitudinal follow-up.

## Data

### Source

- **Dataset**: Midlife in the United States, Wave 2 (MIDUS 2)
- **Collection period**: 2004-2006
- **Sample size**: N=4,963 respondents
- **Design**: Nationally representative sample of English-speaking adults, aged 25-74 at MIDUS 1 (1995-96), re-interviewed at MIDUS 2
- **Instruments**: Phone interview (main survey) + Self-Administered Questionnaire (SAQ)
- **Data access**: ICPSR restricted use contract

### Cross-Sectional Design

All features and outcomes are measured in the same wave (MIDUS 2, 2004-06). There is no longitudinal feature-to-outcome linkage -- the models learn association within a single cross-section, not causal temporal prediction.

| Component | Wave | Year | N | Role |
|-----------|------|------|---|------|
| Features | MIDUS 2 | 2004-06 | 4,963 | Baseline characteristics |
| Outcomes | MIDUS 2 | 2004-06 | 4,963 | Simultaneous outcome measurement |

**Implication**: These models capture population-level correlates, not predictive trajectories. A respondent's "predicted" health_good_excellent probability reflects their demographic and psychological profile, not a future health state.

## Outcomes

### health_good_excellent (binary)

- **Definition**: Respondent reports self-rated health as "Good" or better
- **Source variable**: B1PA1 (Self-Rated Health, MIDUS 2)
- **Coding**: 1 = Excellent, Very Good, or Good (codes 1-3); 0 = Fair or Poor (codes 4-5)
- **Expected prevalence**: ~85-90% (MIDUS 2 mean of 2.46 on 1=excellent to 5=poor scale)
- **Rationale**: Threshold chosen to capture majority-healthful population; binary split at "Good" vs. below reflects clinically meaningful boundary

### high_social_support (binary)

- **Definition**: Respondent scores above midpoint on social support composite
- **Source variable**: B1SCALL (Social Support composite scale, MIDUS 2 SAQ)
- **Coding**: 1 = score > midpoint of scale range; 0 = score at or below midpoint
- **Scale range**: 1-4 (composite of negative and positive support dimensions)
- **Expected prevalence**: ~50-60% (mean ~3.5, skewed toward higher support)
- **Availability**: MIDUS 2 only -- not measured in MIDUS 1 or 3

### high_life_satisfaction (binary)

- **Definition**: Respondent reports life satisfaction above midpoint on 0-10 scale
- **Source variable**: B1SSATIS (Life Satisfaction, MIDUS 2 SAQ)
- **Coding**: 1 = score >= 6; 0 = score < 6
- **Scale range**: 0 (worst possible life) to 10 (best possible life)
- **Expected prevalence**: ~75-80% (mean 7.76, median 8.0 in MIDUS 2)
- **Rationale**: Threshold at 6 captures respondents above "neutral" life evaluation

## Features

All features measured in MIDUS 2 (2004-06).

| Feature | Variable Code | Type | Missingness | Notes |
|---------|--------------|------|-------------|-------|
| Age | B1AGE2 | Continuous (25-74) | <1% | Age at MIDUS 2 interview |
| Sex | B1SEX | Binary (1,2) | <1% | 1=Male, 2=Female |
| Smoking Status | B1DA1 | Categorical | ~2-3% | Current/former/never smoker |
| Alcohol Use | B1DA8A | Continuous | ~3-5% | Drinks per drinking day |
| Physical Activity | B1DA5 | Ordinal | ~4-6% | Frequency of moderate/vigorous activity |
| BMI | B1BMIBR | Continuous | ~8-10% | Derived from self-reported height/weight |
| Personality: Conscientiousness | B1SOPEN6A | Ordinal (1-4) | ~11-14% | SAQ subscale |
| Personality: Neuroticism | B1SNEGA6A | Ordinal (1-4) | ~11-14% | SAQ subscale |
| Perceived Mastery | B1SMASTE | Ordinal (1-7) | ~18% | Pearlin Mastery Scale, SAQ |
| Depressive Symptoms | B1SDEP | Continuous | ~11-15% | CES-D short form, SAQ |

### Feature Engineering

- **Sex**: Binary indicator (0=Male, 1=Female)
- **Age**: Continuous, centered at sample mean for interpretability
- **Smoking**: One-hot encoded (3 dummies: current, former, never)
- **BMI**: Continuous, standardized (z-scored)
- **Physical activity**: Ordinal treated as continuous for logistic regression
- **Personality subscales**: Ordinal (1-4) treated as continuous; each subscale scored as mean of constituent items
- **Mastery**: Ordinal (1-7) treated as continuous
- **Depressive symptoms**: Continuous, standardized
- **Missingness handling**: Listwise deletion for model training; multiple imputation explored as robustness check

### Missingness Pattern

| Feature Group | Missingness Range | Cause |
|---------------|-------------------|-------|
| Demographics (age, sex) | <1% | Near-complete |
| Health behaviors (smoking, alcohol, activity) | 2-6% | Main survey non-response |
| BMI | 8-10% | Height/weight non-report |
| SAQ variables (personality, mastery, depression) | 11-19% | SAQ non-return or incomplete |
| Social support | ~4% | SAQ non-return |

SAQ missingness is the primary data quality concern. Respondents who do not return the SAQ differ systematically from returners (older, less educated, lower income). Listwise deletion on SAQ features reduces effective sample by ~20%.

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
midus2_{outcome}_midus2_baseline_logistic_regression
```

Examples:
- `midus2_health_good_excellent_midus2_baseline_logistic_regression`
- `midus2_high_social_support_midus2_baseline_logistic_regression`
- `midus2_high_life_satisfaction_midus2_baseline_logistic_regression`

## Calibration Metrics

### health_good_excellent

| Metric | CV (5-fold) | Holdout (20%) | Interpretation |
|--------|-------------|---------------|----------------|
| Brier Score | [TBD] | [TBD] | <0.25 reasonable for binary outcome |
| AUC | [TBD] | [TBD] | >0.7 acceptable, >0.8 good |
| Calibration Slope | [TBD] | [TBD] | 1.0 = perfect; <1 = overfit |
| Calibration Intercept | [TBD] | [TBD] | 0.0 = perfect |
| Prevalence (outcome rate) | [TBD] | [TBD] | Base rate in sample (~85-90%) |

### high_social_support

| Metric | CV (5-fold) | Holdout (20%) | Interpretation |
|--------|-------------|---------------|----------------|
| Brier Score | [TBD] | [TBD] | <0.25 reasonable |
| AUC | [TBD] | [TBD] | >0.7 acceptable |
| Calibration Slope | [TBD] | [TBD] | 1.0 = perfect |
| Calibration Intercept | [TBD] | [TBD] | 0.0 = perfect |
| Prevalence (outcome rate) | [TBD] | [TBD] | ~50-60% |

### high_life_satisfaction

| Metric | CV (5-fold) | Holdout (20%) | Interpretation |
|--------|-------------|---------------|----------------|
| Brier Score | [TBD] | [TBD] | <0.25 reasonable |
| AUC | [TBD] | [TBD] | >0.7 acceptable |
| Calibration Slope | [TBD] | [TBD] | 1.0 = perfect |
| Calibration Intercept | [TBD] | [TBD] | 0.0 = perfect |
| Prevalence (outcome rate) | [TBD] | [TBD] | ~75-80% |

### Calibration Curve

Plots of predicted probability vs. observed frequency, binning predictions into deciles. All three models will include calibration curve data (predicted mean per bin vs. observed proportion per bin) as a JSON artifact for frontend visualization.

## Expected Model Behavior

### health_good_excellent

Strongest predictors (expected):
- Age (strong negative relationship -- health declines with age)
- BMI (positive association with poor health)
- Depressive symptoms (strong negative predictor of good health)
- Physical activity (positive predictor of good health)
- Smoking status (current smokers less likely to report good health)

Expected AUC: 0.65-0.75. Self-rated health is strongly associated with demographics and health behaviors, but cross-sectional measurement limits predictive power.

### high_social_support

Strongest predictors (expected):
- Sex (women tend to report higher social support)
- Age (modest positive association)
- Depressive symptoms (negative association -- depression reduces perceived support)
- Conscientiousness (positive association with relationship maintenance)

Expected AUC: 0.60-0.70. Social support is partly trait-like (stable personality component) and partly contextual (current relationships), making cross-sectional prediction moderate.

### high_life_satisfaction

Strongest predictors (expected):
- Perceived mastery (strong positive association -- sense of control predicts satisfaction)
- Depressive symptoms (strong negative association)
- Age (curvilinear -- U-shaped relationship in adulthood)
- Conscientiousness (positive association)
- Physical activity (positive association)

Expected AUC: 0.65-0.75. Life satisfaction is well-predicted by psychological traits (mastery, personality) and mental health indicators, but cross-sectional design limits causal inference.

## Limitations

### Cross-Sectional Design

- **No longitudinal linkage**: All features and outcomes measured simultaneously in MIDUS 2. Models capture association, not prediction over time.
- **Temporal ambiguity**: A respondent with high mastery and high life satisfaction may have mastery causing satisfaction, satisfaction causing mastery, or both caused by a third factor. Cross-sectional data cannot distinguish these.
- **Transfer risk**: These models should not be interpreted as "if you increase mastery, life satisfaction will increase" -- they describe population-level correlates, not intervention effects.

### SAQ Missingness

- **SAQ variables**: 11-19% missing across personality, mastery, depression, and life satisfaction measures
- **SAQ non-response pattern**: Older, less educated, lower-income respondents less likely to return SAQ
- **Impact**: Listwise deletion reduces effective sample; SAQ-dependent features (personality, mastery, depression) cannot be used without accepting ~20% sample reduction
- **Mitigation**: Models with SAQ features use reduced sample (N~3,800-4,200); models without SAQ features use full sample (N~4,900)

### Social Support MIDUS-2-Only

- **Single-wave measurement**: Social support composite (B1SCALL) is only available in MIDUS 2 SAQ
- **No cross-wave validation**: Cannot assess test-retest reliability or stability of social support measurement
- **Construct complexity**: Social support is a multi-dimensional construct (tangible, emotional, informational); composite may obscure dimension-specific patterns

### Cohort Specificity

- **Population**: US adults aged 25-74 at MIDUS 1 (1995-96), re-interviewed at MIDUS 2 (2004-06)
- **Temporal context**: MIDUS 2 data collected pre-Great Recession; economic and social conditions differ from current context
- **Age range**: 34-83 at MIDUS 2 interview; models may not generalize to younger adults (18-30)
- **Transfer risk**: MEDIUM for health and wellbeing (stable constructs); HIGH for relationship (single-wave, complex construct)

### Methodological

- **Logistic regression**: Linear decision boundary in log-odds space; may miss non-linear interactions
- **No regularization**: Baseline models use vanilla logistic regression; overfitting risk with 10 features
- **Single split**: Results depend on random seed; 5-fold CV mitigates but does not eliminate this
- **Outcome thresholds**: Binary splits at specific thresholds (e.g., life satisfaction >= 6) are arbitrary; sensitivity to threshold choice should be tested

## Transfer Risk Assessment

| Domain | Risk Level | Rationale |
|--------|-----------|-----------|
| Health | MEDIUM | Self-rated health is stable and well-measured (<1% missing), but cross-sectional design limits causal interpretation. Age and health behavior associations are robust across studies. |
| Subjective Wellbeing | MEDIUM | Life satisfaction and mastery are stable psychological constructs with good measurement properties. SAQ missingness is the primary concern, not construct instability. |
| Relationship | HIGH | Social support is measured in a single wave only (MIDUS 2), with complex multi-dimensional construct. No cross-wave validation possible. Social support may reflect current relationship state rather than stable trait. |

## Route B Approval Criteria

These models are candidates for Route B approval as `calibrated_model` artifacts. All criteria must be satisfied:

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Actual data used (not literature-only) | [ ] | MIDUS 2 SPSS files confirmed via pyreadstat |
| Variable codes confirmed in raw data | [ ] | B1PA1, B1SCALL, B1SSATIS, B1AGE2, B1SEX, etc. |
| Feature-outcome measurement documented | [ ] | Cross-sectional, same-wave measurement |
| Model trained with documented protocol | [ ] | Logistic regression, 80/20 split, 5-fold CV |
| Calibration metrics reported | [ ] | Brier, AUC, calibration slope/intercept |
| Calibration curve available | [ ] | Decile-binned predicted vs. observed |
| Model card completed | [ ] | See template fields below |
| Transfer risk documented | [ ] | MEDIUM (health, wellbeing), HIGH (relationship) |
| Safety checks passed | [ ] | No raw data, no individual predictions |

### Approval Gate

Models meet Route B approval when:
1. All metrics are computed and documented (TBD values filled)
2. Calibration slope is within [0.7, 1.3] (no severe miscalibration)
3. AUC exceeds 0.65 for all three outcomes
4. Brier score is below 0.25 for all three outcomes
5. Model card is complete with all required fields
6. Cross-sectional limitation is prominently documented in model card

## Safety Confirmations

- **No raw data committed**: Only aggregate statistics, model coefficients, and evaluation metrics stored in repository
- **No individual predictions**: Models emit population-level probability distributions, not individual-level risk scores
- **No life_score integration**: These priors inform branch forecasts; they do not compute or modify life scores
- **No PII in outputs**: Respondent IDs used during training only; not stored in model artifacts
- **Audit trail**: Model cards document training data, protocol, and metrics for reproducibility
- **Cross-sectional caveat**: All model cards include prominent note that associations are cross-sectional, not longitudinal predictions

## Artifact Locations

- **Model coefficients**: `labs/population_baseline/artifacts/midus2_*_coefficients.json` (after training)
- **Evaluation metrics**: `labs/population_baseline/artifacts/midus2_*_metrics.json` (after training)
- **Calibration curves**: `labs/population_baseline/artifacts/midus2_*_calibration.json` (after training)
- **Model cards**: `labs/population_baseline/artifacts/midus2_*_model_card.json` (after training)

## Model Card Fields

Following `model_card_template.md`, each model card includes:

```json
{
  "model_id": "midus2_health_good_excellent_midus2_baseline_logistic_regression",
  "source_dataset": "midus2",
  "outcome": "health_good_excellent",
  "features": ["age", "sex", "smoking_status", "alcohol_use", "physical_activity", "bmi", "conscientiousness", "neuroticism", "mastery", "depressive_symptoms"],
  "model_family": "logistic_regression",
  "training_status": "not_trained",
  "training_date": null,
  "training_sample_size": null,
  "split": "80/20 stratified",
  "cv_folds": 5,
  "design": "cross-sectional",
  "metrics": {
    "brier_score": null,
    "auc": null,
    "calibration_slope": null,
    "calibration_intercept": null
  },
  "transfer_risk": "medium",
  "transfer_rationale": "Cross-sectional association, not longitudinal prediction. US adults 34-83 in 2004-06. Stable constructs but no temporal validation.",
  "approved_for_route_b": false,
  "approval_conditions": "Requires computed metrics meeting threshold criteria and cross-sectional limitation documentation"
}
```

## Comparison with NLSY97 Models

| Dimension | NLSY97 v3 | MIDUS v3 |
|-----------|-----------|----------|
| Design | Longitudinal (2005 -> 2015) | Cross-sectional (2004-06 only) |
| Temporal prediction | 10-year follow-up | None (same-wave association) |
| Sample size | 50,000 (from 89,814) | 4,963 |
| Features | Education, sex, race | Age, sex, health behaviors, personality, mastery |
| Outcomes | Education degree, income | Health, social support, life satisfaction |
| Transfer risk | HIGH (cohort-specific) | MEDIUM-HIGH (construct-dependent) |
| Causal inference | Stronger (temporal ordering) | Weaker (cross-sectional) |

MIDUS v3 models complement NLSY97 v3 by covering different domains (health, wellbeing, relationships vs. education, income) but with weaker temporal design. Both are needed for comprehensive Route B coverage across 5 domains.

## Next Steps

1. **Training**: Run logistic regression on MIDUS 2 data for all three outcomes
2. **Evaluation**: Compute Brier, AUC, calibration metrics on holdout set
3. **Calibration curves**: Generate decile-binned predicted vs. observed data
4. **Model cards**: Complete model card JSON for all three outcomes
5. **Threshold sensitivity**: Test alternative outcome thresholds (e.g., life satisfaction >= 7 vs. >= 6)
6. **SAQ robustness**: Compare models with and without SAQ features (different sample sizes)
7. **Approval review**: Submit for Route B approval gate
8. **Elastic net variants**: Train regularized variants as robustness check
