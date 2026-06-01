# Model Card Template — Population Baseline

Use this template when creating a new population baseline model. Every field is required unless marked optional.

---

## Model Identity

- **Model ID**: `{source_dataset}_{outcome_id}_{model_family}` (e.g., `nlsy79_income_above_median_logistic_regression`)
- **Source Dataset(s)**: [list source_ids from dataset registry]
- **Outcome**: [outcome_id from outcome definitions]
- **Feature Mappings**: [list feature_ids from feature mapping]
- **Model Family**: [logistic_regression | elastic_net | ordinal_regression | survival_model | baseline_table | literature_prior_only]

## Training Status

- **Status**: [not_trained | trained | validated | rejected]
- **Training date**: [YYYY-MM-DD or N/A]
- **Training sample size**: [N or N/A]
- **Training/validation split**: [e.g., 80/20 or N/A]

## Evaluation Summary

[Free text description of how the model was evaluated. Include out-of-sample methodology.]

## Calibration Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Brier Score | [0.0-1.0 or N/A] | Lower is better. <0.25 is reasonable for binary outcomes. |
| Calibration Slope | [float or N/A] | 1.0 is perfectly calibrated. <1 = overfit, >1 = underfit. |
| Calibration Intercept | [float or N/A] | 0.0 is perfectly calibrated. |
| AUC / C-statistic | [0.0-1.0 or N/A] | Discrimination ability. >0.7 is acceptable. |
| R² | [0.0-1.0 or N/A] | Variance explained (for continuous outcomes). |

## Transfer Risk Assessment

- **Risk level**: [low | medium | high]
- **Rationale**: [Why this level? Consider population overlap, temporal gap, cultural context.]
- **Population mismatch**: [Describe how the training population differs from the target user.]

## Approval

- **Approved for Route B**: [true | false]
- **Approval date**: [YYYY-MM-DD or N/A]
- **Approval conditions**: [Any caps, warnings, or restrictions.]

## Limitations

[List all known limitations: sample restrictions, variable definitions, missing data, potential biases.]

## Prior Generation Rules

- `approved_for_route_b = false` → no numeric priors, no probability bands
- `approved_for_route_b = true` + `training_status != validated` → textual priors only
- `approved_for_route_b = true` + `training_status = validated` → probability bands allowed
- `transfer_risk = high` → confidence capped at medium
- `model_family = literature_prior_only` → textual priors only, no numeric outputs

---

**Note**: This model card is a required artifact for any population prior that enters the main forecast system. Without a completed model card, the integration contract (`PublicPriorIntegrationContract`) will reject the prior.
