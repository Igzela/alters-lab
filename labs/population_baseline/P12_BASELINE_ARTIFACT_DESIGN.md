# Phase 12E — Baseline Artifact Design

## Summary

Defines two artifact types for the population baseline pilot: **baseline_table** (pre-ML descriptive statistics) and **model_card_candidate** (placeholder for future ML models).

## Artifact Type 1: baseline_table

### Purpose
Descriptive population statistics before any ML model is trained. Provides base rates, means, and confidence intervals for each outcome by subgroup.

### When to Use
- Before any model training
- To establish population-level reference points
- To identify outcomes with sufficient data for modeling
- To assess subgroup sample sizes

### Fields

| Field | Type | Description |
|-------|------|-------------|
| artifact_id | string | Unique identifier (e.g., `bt_nlsy97_employment_stability_2010`) |
| dataset_source_id | string | Source dataset (nlsy97 or midus) |
| outcome_id | string | Outcome being measured |
| subgroup_definition | string | How the subgroup is defined (e.g., "age 25-34, male") |
| n | integer | Sample size for this subgroup |
| observed_rate_or_mean | float | Observed rate (binary) or mean (continuous) |
| confidence_interval | string | 95% CI (e.g., "0.52-0.58" or "3.1-3.4") |
| missingness_rate | float | Fraction of eligible cases with missing outcome data |
| transfer_risk | string | low/medium/high |
| limitations | list[string] | Known limitations for this specific artifact |

### Example (hypothetical)
```yaml
artifact_id: bt_nlsy97_employment_stability_2010_age2534
dataset_source_id: nlsy97
outcome_id: employment_stability
subgroup_definition: "age 25-34, all genders, all education levels"
n: 3204
observed_rate_or_mean: 0.68
confidence_interval: "0.66-0.70"
missingness_rate: 0.12
transfer_risk: high
limitations:
  - "Cohort born 1980-84, not directly comparable to current young adults"
  - "US-only, self-reported employment"
```

### Constraints
- No exact personal probabilities
- No life_score
- No model_card or route_b approval
- Purely descriptive statistics

## Artifact Type 2: model_card_candidate

### Purpose
Placeholder model card for future ML models. No model is trained in Phase 12. This defines the structure that must be filled before any model enters the forecast path.

### When to Use
- After baseline_table validation
- If a lightweight interpretable model is considered
- Only after all baseline tables are reviewed and approved

### Fields

| Field | Type | Description |
|-------|------|-------------|
| model_id | string | Unique identifier |
| dataset_source_ids | list[string] | Source datasets used |
| outcome_id | string | Outcome being predicted |
| feature_mapping_ids | list[string] | Feature mappings used |
| model_family | string | logistic_regression / elastic_net / ordinal_regression / survival_model / baseline_table / literature_prior_only |
| training_status | string | not_trained (always, in Phase 12) |
| approved_for_route_b | bool | false (always, in Phase 12) |
| required_validation_before_approval | list[string] | Gates that must pass |
| calibration_metrics | object | All null in Phase 12 |
| limitations | list[string] | Known limitations |

### Example (Phase 12 placeholder)
```yaml
model_id: mc_nlsy97_employment_stability_v0
dataset_source_ids: [nlsy97]
outcome_id: employment_stability
feature_mapping_ids: [education_status, employment_status, financial_stability]
model_family: baseline_table
training_status: not_trained
approved_for_route_b: false
required_validation_before_approval:
  - "out_of_sample_calibration"
  - "transfer_risk_assessment"
  - "cross_validation_brier_score"
  - "subgroup_fairness_check"
calibration_metrics:
  brier_score: null
  calibration_slope: null
  calibration_intercept: null
  auc: null
  r2: null
limitations:
  - "No model trained in Phase 12"
  - "Baseline table only — no predictive claims"
```

## Design Principles

1. **baseline_table first**: Always build descriptive baselines before considering any ML model
2. **model_card_candidate is a placeholder**: No training happens in Phase 12
3. **No route_b approval**: Phase 12 artifacts cannot enter the production forecast path
4. **No exact probabilities**: Only rates, means, and confidence intervals
5. **Transfer risk always labeled**: Every artifact carries a transfer_risk field
6. **Limitations always listed**: Every artifact documents what it does NOT capture

## Validation Path

```
Phase 12: Build baseline_table artifacts
    ↓
Phase 13 (future): Validate baseline tables, assess data quality
    ↓
Phase 14 (future): Train lightweight interpretable models
    ↓
Phase 15 (future): Submit model_card for validation gate review
    ↓
If approved: model_card enters Route B with approved_for_route_b = true
```

## Config File

See `config/baseline_artifact_schema_p12.yaml` for structured definitions.
