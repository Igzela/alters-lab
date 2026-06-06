# Data Model

All data is stored as YAML/JSON files under `alters/`. No database. Pydantic schemas in `apps/api/src/alters_lab/schemas/` enforce structure and invariants.

## Directory Structure

```
alters/
  current/                    # Active working data (user-specific, gitignored)
    snapshot.yaml             # Current life state
    branches.yaml             # Discovered branches
    reality_trace.yaml        # Reality vs. prediction tracking
    alters/                   # alter_A.yaml through alter_D.yaml
    dialogue/                 # Dialogue session records
    value_alignment/          # Value alignment reports
  sample/                     # Sample data for new users (checked in)
    snapshot.yaml, branches.yaml, alters/, reality_trace.yaml
  calibration/                # Evaluation framework
    rubric.yaml               # 4-axis evaluation rubric
    state.json                # Calibration cycle state
    scores/                   # Per-cycle score records
    rubric_delta_suggestions/ # Rubric evolution suggestions
    checkpoint_plans/         # Checkpoint regeneration plans
  product/                    # Runtime product data
    config/                   # config.yaml, secrets.yaml
    weekly_notes/             # Ingested weekly notes
    weekly_reviews/           # Weekly review sessions
    calibration_records/      # Action alignment scores
    pattern_reviews/          # Behavioral pattern analysis
    behavior_validation/      # Validation reports
    behavior_metrics/         # Weekly behavioral indicators
      catalog/                # Metric definitions (behavior_metric_set_v0_2.yaml)
      raw_events/             # Raw event data (future)
      weekly_records/         # Weekly behavior metric records
      summaries/              # Aggregated summaries (future)
    branch_milestones/        # Branch milestone records
    sessions/                 # Provider dialogue sessions
    provider_runs/            # Provider call logs
    exports/                  # Data exports
  archive/                    # Completed cycle archives
```

## Core Entities

### Snapshot (`snapshot.yaml`)

Top-level key: `snapshot:`. Contains the user's current life state.

| Field | Type | Description |
|-------|------|-------------|
| `date` | string \| null | Snapshot date |
| `version` | int | Schema version (>= 1) |
| `anchors` | SnapshotAnchors | Three core anchors |
| `context` | SnapshotContext | Commitments, deadlines, energy |
| `intake_status` | SnapshotIntakeStatus | Phase and completion tracking |
| `evidence_policy` | EvidencePolicy | Source mode and confidence |
| `notes` | list[str] | Freeform notes |

**SnapshotAnchors:**
| Field | Type |
|-------|------|
| `heaviest_constraint` | str |
| `most_unclear` | str |
| `unwilling_to_give_up` | str |

**SnapshotContext:**
| Field | Type |
|-------|------|
| `current_commitments` | list[str] |
| `external_deadlines` | list[str] |
| `energy_state` | str |

**SnapshotIntakeStatus:**
| Field | Type |
|-------|------|
| `phase` | Enum: `not_started`, `asking_heaviest_constraint`, `asking_most_unclear`, `asking_unwilling_to_give_up`, `ready_for_snapshot_confirmation`, `completed` |
| `completed_anchors` | list[AnchorName] |
| `pending_anchor` | AnchorName \| null |

### Branch (`branches.yaml`)

Top-level key: `branch_discovery:` + `branches:`.

**BranchDiscoveryStatus:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | `"not_started"` or `"completed"` |
| `source_snapshot_ref` | str | Path to source snapshot |
| `requires_snapshot_phase` | str | Required snapshot phase |
| `confirmed_by` | str | Who confirmed |
| `confirmation_note` | str | Confirmation note |

**Branch:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | str | `branch_A` through `branch_D` |
| `label` | str | Human-readable label |
| `core_choice` | str | The fundamental choice this branch represents |
| `structural_commitment` | str | What must be committed |
| `key_tension_resolved` | str | Which tension this branch resolves |
| `incompatible_with` | list[str] | Other branch IDs this is incompatible with |
| `preserves` | list[str] | What this branch preserves |
| `sacrifices` | list[str] | What this branch sacrifices |
| `validation_signal_30d` | list[str] | Signals to watch in 30 days |
| `invalid_if` | list[str] | Conditions that invalidate this branch |

### Alter (`alters/alter_A.yaml` through `alter_D.yaml`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | `alter_A` through `alter_D` (enforced) |
| `branch_ref` | str | Must match: `alter_A` → `branch_A` |
| `label` | str | Alter's name |
| `source_refs` | AlterSourceRefs | References to source files |
| `quality_status` | AlterQualityStatus | Confirmation and active status |
| `voice` | AlterVoice | Personality and stance |

**AlterSourceRefs** (all paths enforced by validator):
| Field | Required Value |
|-------|---------------|
| `snapshot_ref` | `"alters/current/snapshot.yaml"` |
| `branches_ref` | `"alters/current/branches.yaml"` |
| `rubric_ref` | `"alters/calibration/rubric.yaml"` |

**AlterQualityStatus:**
| Field | Type |
|-------|------|
| `human_confirmed` | bool (must be `true`) |
| `active` | bool (must be `true`) |
| `notes` | list[str] |

**AlterVoice:**
| Field | Type |
|-------|------|
| `core_stance` | str (must be non-empty) |
| `typical_concern` | str |
| `decision_style` | str |
| `self_warning` | str |

### Rubric (`calibration/rubric.yaml`)

4-axis evaluation framework. `auto_modify` is always `false`.

### RealityTrace (`current/reality_trace.yaml`)

Tracks how reality diverges from branch predictions over time.

### ActionAlignmentScore (`product/calibration_records/`)

Weekly review scoring: direction alignment, execution consistency, avoidance level, verdict label.

### WeeklyReviewSession (`product/weekly_reviews/`)

Complete weekly review session with review note, dialogue summary, primary correction, supporting actions.

### WeeklyNoteExtractedRecord (`product/weekly_notes/`)

Ingested and parsed weekly note from Obsidian. Stores the raw note and extracted structured fields.

| Field | Type | Description |
|-------|------|-------------|
| `record_id` | str | Unique identifier |
| `source_type` | Literal["obsidian_weekly_note"] | Always this value |
| `raw_note_preserved` | Literal[True] | Raw note is preserved |
| `derived_from_raw_note` | Literal[True] | Record is derived from raw note |
| `source_path` | str \| null | Original file path |
| `raw_note` | str | Original raw note text |
| `session_type` | SessionType | One of: `personal`, `project`, `learning`, `relationship` |
| `observable_facts` | list[str] | 5-7 extracted facts |
| `subjective_state` | str | How the user feels |
| `primary_problem` | str | Main issue identified |
| `friction_or_avoidance_point` | str | What's being avoided |
| `desired_correction` | str | What the user wants to change |
| `extraction_warnings` | list[str] | Warnings from extraction |
| `edit_history` | list[WeeklyNoteEditDiff] | History of edits |
| `created_at` | str | Creation timestamp |
| `updated_at` | str \| null | Last update timestamp |

### ProviderConfig (`product/config/config.yaml`)

Provider configuration for LLM integration. Controls mode, endpoint, model, and safety flags.

| Field | Type | Description |
|-------|------|-------------|
| `mode` | ProviderMode | `disabled`, `mock`, or `openai-compatible-http` |
| `base_url` | str \| null | API endpoint URL |
| `model` | str \| null | Model name |
| `timeout_seconds` | int | Request timeout (1-600) |
| `secret_storage` | SecretStorage | `keyring` or `secrets_yaml_fallback` |
| `key_name` | str | Keyring key name |

**ProviderSafetyFlags** (returned in status responses):
| Field | Type | Description |
|-------|------|-------------|
| `provider_output_persists_by_default` | Literal[False] | Output persistence disabled |
| `provider_output_can_write_active_yaml` | Literal[False] | Cannot modify active YAML |
| `provider_output_can_generate_reality_score` | Literal[False] | Cannot generate scores |
| `behavior_validated` | Literal[False] | Behavior not yet validated |
| `p6_sealed` | Literal[False] | P6 not yet sealed |

### PatternReviewRecord (`product/pattern_reviews/`)

Four-week pattern review analyzing behavioral patterns across multiple weeks.

| Field | Type | Description |
|-------|------|-------------|
| `review_id` | str | Unique identifier |
| `status` | Literal["insufficient_data", "no_pattern", "pattern_triggered"] | Review outcome |
| `weeks_evaluated` | int | Number of weeks analyzed |
| `triggered_patterns` | list[TriggeredPattern] | Patterns that were triggered |
| `created_at` | str | Creation timestamp |
| `active_yaml_modified` | bool | Whether active YAML was modified |
| `provider_called` | bool | Whether provider was called |

**TriggeredPattern:**
| Field | Type | Description |
|-------|------|-------------|
| `pattern` | PatternName | Pattern identifier |
| `occurrences` | int | Number of occurrences |
| `confidence` | float | Confidence score (0-1) |
| `strategy_constraint` | str | Constraint for this pattern |

**PatternName** values:
- `repeated_noisy_progress`
- `repeated_avoidance_disguised_as_work`
- `repeated_sleep_breakdown`
- `repeated_over_scope`
- `repeated_action_mismatch`
- `repeated_primary_correction_failure`

## Behavior Metrics Schemas

### WeeklyBehaviorMetricsRecord (`product/behavior_metrics/weekly_records/`)

Weekly aggregate of observable behavioral indicators. User-entered data; no LLM boundary audit fields.

| Field | Type | Description |
|-------|------|-------------|
| `record_id` | str | Unique identifier |
| `week_start` | date | Week start date (Monday) |
| `week_end` | date | Week end date (Sunday) |
| `branch_id` | str \| None | Associated branch |
| `milestone_id` | str \| None | Associated milestone (required if key_milestone_progress_pct > 0) |
| `milestone_observable_evidence` | str \| None | Evidence of milestone progress |
| `career_education_deep_work_minutes` | int (≥0) | Deep work minutes |
| `planned_commitment_follow_through_rate` | float (0–1) | Commitment completion ratio |
| `expense_logged_days` | int (0–7) | Days expenses were logged |
| `regular_sleep_nights` | int (0–7) | Nights with regular sleep |
| `moderate_vigorous_activity_minutes` | int (≥0) | Physical activity minutes |
| `avoidable_health_risk_events` | int (≥0) | Health risk events (lower is better) |
| `meaningful_social_contact_count` | int (≥0) | Meaningful social interactions |
| `abandoned_committed_blocks` | int (≥0) | Abandoned time blocks (lower is better) |
| `key_milestone_progress_pct` | float (0–1) | Milestone progress ratio |
| `missing_metrics` | dict[str, MissingReason] | Metrics explicitly not tracked |
| `source_quality` | SourceQuality | Data source quality |
| `notes` | str | Free-text notes |

**MissingReason** values: `not_tracked`, `not_applicable`, `device_failure`, `user_skipped`, `unknown`
**SourceQuality** values: `manual`, `mixed`, `device_assisted`

**Metric ID → Field mapping** (`METRIC_ID_TO_FIELD`):
| Metric ID | Record Field |
|-----------|-------------|
| `career_education_deep_work_minutes` | `career_education_deep_work_minutes` |
| `planned_commitment_follow_through_rate` | `planned_commitment_follow_through_rate` |
| `financial_planfulness` | `expense_logged_days` |
| `sleep_regular_nights` | `regular_sleep_nights` |
| `moderate_vigorous_activity_minutes` | `moderate_vigorous_activity_minutes` |
| `avoidable_health_risk_events` | `avoidable_health_risk_events` |
| `meaningful_social_contact_count` | `meaningful_social_contact_count` |
| `abandoned_committed_blocks` | `abandoned_committed_blocks` |
| `key_milestone_progress` | `key_milestone_progress_pct` |

### BranchMilestoneRecord (`product/branch_milestones/`)

| Field | Type | Description |
|-------|------|-------------|
| `milestone_id` | str | Unique identifier |
| `branch_id` | str | Parent branch |
| `title` | str | Milestone title |
| `description` | str | Description |
| `target_completion_date` | date | Target date |
| `observable_done_definition` | str | Observable completion criteria |
| `status` | Literal["planned", "active", "completed", "abandoned"] | Status |
| `created_at` | str | Creation timestamp |

### BehaviorMetricTrendResult

Within-person trend analysis for a single metric. Route A only; Route B fields are placeholders.

| Field | Type | Description |
|-------|------|-------------|
| `metric_id` | str | Metric identifier |
| `direction` | Literal["improving", "declining", "stable", "insufficient_data"] | Trend direction |
| `slope` | float | Linear slope |
| `confidence_level` | Literal["low", "medium", "high"] | Confidence based on data points |
| `data_points` | int | Valid data points used |
| `current_value` | float \| int \| None | Most recent value |
| `rolling_4w_median` | float \| None | 4-week rolling median |
| `population_percentile` | float \| None | Route B placeholder (always None) |
| `deviation_from_baseline` | float \| None | Route B placeholder (always None) |
| `route_a_available` | bool | Always True |
| `route_b_available` | bool | Always False |

## Trend Analysis Schemas

### TrendAnalysisResult

Output of trend analysis — linear extrapolation from historical action alignment scores.

| Field | Type | Description |
|-------|------|-------------|
| `status` | str | Always "ok" |
| `overall_direction` | Literal["improving", "declining", "stable", "insufficient_data"] | Overall trend direction |
| `dimensions` | list[TrendDimensionResult] | Per-dimension trend analysis |
| `forecast` | list[ForecastPoint] | Predicted scores for future weeks |
| `confidence_interval` | ConfidenceInterval | Confidence level and description |
| `generated_at` | str | Generation timestamp |

**ForecastPoint:**
| Field | Type | Description |
|-------|------|-------------|
| `week_offset` | int | Weeks into future (1-12) |
| `predicted_score` | float | Predicted alignment score (0-1) |
| `lower_bound` | float | Lower confidence bound (0-1) |
| `upper_bound` | float | Upper confidence bound (0-1) |

**ConfidenceInterval:**
| Field | Type | Description |
|-------|------|-------------|
| `level` | Literal["low", "medium", "high"] | Confidence level |
| `data_count` | int | Number of data points used |
| `consistency_score` | float | Data consistency (0-1) |
| `description` | str | Human-readable confidence description |

### DynamicWeightResult

Advisory rubric dimension weights based on current behavioral state.

| Field | Type | Description |
|-------|------|-------------|
| `status` | str | Always "ok" |
| `weights` | list[DimensionWeight] | Per-dimension weight recommendations |
| `overall_alignment` | float | Average alignment score (0-1) |
| `recommendation` | str | Human-readable recommendation |
| `generated_at` | str | Generation timestamp |

**DimensionWeight:**
| Field | Type | Description |
|-------|------|-------------|
| `dimension` | str | Rubric dimension name |
| `weight` | float | Advisory weight (0.5-2.0) |
| `rationale` | str | Why this weight was chosen |

### PatternAdjustmentResult

Forecast adjusted based on detected behavioral patterns.

| Field | Type | Description |
|-------|------|-------------|
| `status` | str | Always "ok" |
| `has_patterns` | bool | Whether any patterns were detected |
| `original_forecast` | list[ForecastPoint] | Unadjusted forecast |
| `adjusted_forecast` | list[AdjustedForecastPoint] | Pattern-adjusted forecast |
| `adjustments_applied` | list[str] | Pattern names that were applied |
| `generated_at` | str | Generation timestamp |

**AdjustedForecastPoint:**
| Field | Type | Description |
|-------|------|-------------|
| `week_offset` | int | Weeks into future (1-12) |
| `original_score` | float | Original predicted score (0-1) |
| `adjusted_score` | float | Pattern-adjusted score (0-1) |
| `adjustment_delta` | float | Change from original (negative = dampening) |
| `adjustment_reason` | str | Why this adjustment was made |
| `lower_bound` | float | Lower confidence bound (0-1) |
| `upper_bound` | float | Upper confidence bound (0-1) |

## Key Invariants

- **extra="forbid"**: Most Pydantic models reject unknown fields. YAML files on disk may have extra fields, but API validation is strict.
- **Alter IDs**: Must be exactly `alter_A`, `alter_B`, `alter_C`, `alter_D`.
- **Branch refs**: `alter_A` must reference `branch_A`, etc.
- **Source refs**: Must point to exact paths (`alters/current/snapshot.yaml`, etc.).
- **Completion validation**: Completed snapshots require all three anchors filled and `pending_anchor: null`. Completed branch discovery requires exactly 4 branches.
- **Mutual incompatibility**: Each branch must have non-empty `incompatible_with` listing the other 3 branch IDs.
- **Rubric immutability**: `auto_modify` is always `false`. Rubric changes require explicit human approval.
- **Approval tokens**: Write operations require an `approval_token` — a domain-specific safety gate, not HTTP auth.

## Population Baseline Schemas (Phase 11)

Location: `apps/api/src/alters_lab/schemas/population_baseline.py`

These schemas define the offline Population Baseline Lab. They are not used in the main forecast path — they define how public datasets can produce auditable baseline priors.

### PublicDatasetSource

A public dataset or literature source used for population baselines.

| Field | Type | Description |
|-------|------|-------------|
| `source_id` | str | Unique identifier |
| `label` | str | Human-readable name |
| `source_type` | Literal | longitudinal_dataset, panel_dataset, benchmark_dataset, literature_review, meta_analysis |
| `access_url` | str \| None | URL to access the dataset |
| `access_notes` | str | How to access the data |
| `population_description` | str | Description of the study population |
| `time_horizon` | str | Duration of follow-up |
| `available_domains` | list[Domain] | Which domains the dataset covers |
| `transfer_risk` | Literal | low, medium, high |
| `allowed_use` | Literal | research_only, prior_generation, documentation_only |
| `notes` | str | Additional notes |

### PublicOutcomeDefinition

An externally defined outcome used to evaluate forecasts.

| Field | Type | Description |
|-------|------|-------------|
| `outcome_id` | str | Unique identifier |
| `domain` | Domain | One of the 5 domains |
| `label` | str | Human-readable name |
| `definition` | str | Operational definition |
| `time_horizon_months` | int \| None | Time horizon for measurement |
| `measurement_type` | Literal | binary, ordinal, continuous, survival, categorical |
| `dataset_source_ids` | list[str] | Which datasets have this outcome |
| `limitations` | list[str] | Known limitations |

### PublicFeatureMapping

Maps public dataset variables to internal predictor/behavior fields.

| Field | Type | Description |
|-------|------|-------------|
| `feature_id` | str | Unique identifier |
| `construct_id` | str | The underlying construct |
| `label` | str | Human-readable name |
| `source_variable_names` | list[str] | Variable names in source datasets |
| `maps_to_predictor_profile_fields` | list[str] | Which predictor profile fields this maps to |
| `maps_to_behavior_metric_ids` | list[str] | Which behavior metrics this maps to |
| `expected_direction` | Literal | positive, negative, mixed, unknown |
| `transformation_notes` | str | How to transform the variable |
| `missingness_notes` | str | Known missing data patterns |
| `transfer_risk` | Literal | low, medium, high |

### CalibrationMetrics

Sub-model for model calibration metrics.

| Field | Type | Description |
|-------|------|-------------|
| `brier_score` | float \| None | Brier score (lower is better) |
| `calibration_slope` | float \| None | Should be near 1.0 |
| `calibration_intercept` | float \| None | Should be near 0.0 |
| `auc` | float \| None | Area under ROC curve |
| `r2` | float \| None | R-squared (continuous outcomes) |

### PopulationBaselineModelCard

Model card for a population baseline model artifact.

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | str | Unique identifier |
| `source_dataset_ids` | list[str] | Training datasets |
| `outcome_id` | str | Target outcome |
| `feature_mapping_ids` | list[str] | Features used |
| `model_family` | Literal | logistic_regression, elastic_net, ordinal_regression, survival_model, baseline_table, literature_prior_only |
| `training_status` | Literal | not_trained, trained, validated, rejected |
| `evaluation_summary` | str | How the model was evaluated |
| `calibration_metrics` | CalibrationMetrics | Calibration quality metrics |
| `transfer_risk` | Literal | low, medium, high |
| `approved_for_route_b` | bool | Whether this model can produce priors (default: false) |
| `limitations` | list[str] | Known limitations |

### PopulationPriorArtifact

A prior derived from a population baseline model.

| Field | Type | Description |
|-------|------|-------------|
| `artifact_id` | str | Unique identifier |
| `model_id` | str | Source model |
| `generated_at` | str | When the artifact was generated |
| `domain` | Domain | Which domain this prior covers |
| `prior_type` | Literal | textual, probability_band, percentile, baseline_table |
| `prior_direction` | Literal | favorable, unfavorable, mixed, unknown |
| `probability_band` | str \| None | Probability range (requires approved model) |
| `population_percentile` | float \| None | Percentile (requires numeric baseline) |
| `deviation_from_baseline` | float \| None | Deviation from population baseline |
| `confidence` | Literal | low, medium, high (capped if high transfer risk) |
| `transfer_risk` | Literal | low, medium, high |
| `explanation` | str | Human-readable explanation |
| `limitations` | list[str] | Known limitations |

**Guardrails:**
- High transfer_risk caps confidence at medium
- No numeric priors without approved model card
- `literature_prior_only` models produce textual priors only

## Public Prior Integration Contract (Phase 11)

Location: `apps/api/src/alters_lab/schemas/public_prior_contract.py`

Defines how population baseline outputs may enter the main forecast system.

### PublicPriorIntegrationContract

| Field | Type | Description |
|-------|------|-------------|
| `contract_id` | str | Contract identifier |
| `version` | str | Contract version |
| `allowed_input_artifacts` | list[str] | Artifact types allowed as input |
| `allowed_output_fields` | list[str] | Fields that may appear in forecast output |
| `required_guards` | list[str] | Validation guards that must pass |
| `disallowed_behaviors` | list[str] | Behaviors that are explicitly prohibited |

**Module-level constants:** `ALLOWED_OUTPUT_FIELDS`, `REQUIRED_GUARDS`, `DISALLOWED_BEHAVIORS` available for import.

## Personal Prior Adapter (Route B v4)

Location: `apps/api/src/alters_lab/schemas/personal_prior_adapter.py`

Combines Route A personal evidence, Route B public priors, external evidence, and behavior metric completeness into per-domain adapted forecasts. See `docs/PERSONAL_PRIOR_ADAPTER_POLICY.md` for the full policy.

### EvidenceComponent

A single evidence input to the adapter.

| Field | Type | Description |
|-------|------|-------------|
| `source` | Literal | route_a_behavior, route_b_public_prior, external_evidence, outcome_target, calibration_history, contextual_prior |
| `domain` | Domain | One of the 5 domains |
| `direction` | Literal | improving, declining, stable, mixed, unknown |
| `strength` | Literal | weak, medium, strong |
| `confidence` | Literal | low, medium, high |
| `freshness_days` | int \| None | Days since evidence was collected |
| `explanation` | str | Human-readable explanation |
| `limitations` | list[str] | Known limitations |

### PersonalPriorAdapterResult

Per-domain adapter result combining all evidence sources.

| Field | Type | Description |
|-------|------|-------------|
| `domain` | Domain | One of the 5 domains |
| `route_a_direction` | Literal | Personal evidence direction |
| `route_b_direction` | Literal | Public prior direction |
| `route_b_strength_level` | Literal | strong_calibrated, data_backed, contextual, unavailable |
| `external_evidence_direction` | Literal | External evidence direction |
| `alignment` | Literal | aligned, conflicted, route_a_only, route_b_only, insufficient_data |
| `conflict_level` | Literal | none, low, medium, high |
| `adjusted_forecast_direction` | Literal | Final adapted direction |
| `adjusted_confidence` | Literal | Final adapted confidence |
| `confidence_drivers` | list[str] | What increased confidence |
| `confidence_penalties` | list[str] | What decreased confidence |
| `next_evidence_to_collect` | list[str] | Suggestions for improving the forecast |
| `explanation` | str | Human-readable explanation |

### PersonalPriorAdapterSummary

Aggregate adapter result across all domains.

| Field | Type | Description |
|-------|------|-------------|
| `domain_results` | list[PersonalPriorAdapterResult] | Per-domain results |
| `overall_alignment` | Literal | aligned, conflicted, mixed, insufficient_data |
| `overall_conflict_level` | Literal | none, low, medium, high |
| `forecast_readiness` | Literal | insufficient, provisional, usable, strong |
| `readiness_reasons` | list[str] | Why readiness is at this level |
| `readiness_blockers` | list[str] | What blocks higher readiness |
| `evidence_components` | list[EvidenceComponent] | All evidence inputs used |

### SourceHitRates (CalibrationScorecard extension)

Per-source hit rates for comparing Route A, Route B, and Adapter accuracy.

| Field | Type | Description |
|-------|------|-------------|
| `route_a_hit/miss/partial/unknown_count` | int | Route A match counts |
| `route_b_hit/miss/partial/unknown_count` | int | Route B match counts |
| `adapter_hit/miss/partial/unknown_count` | int | Adapter match counts |
| `conflict_outcomes` | dict[str, int] | Conflict level → match result counts |

## LLM-Driven Calibration

### CalibrationConversation (`product/calibration_conversations/`)

A conversation session between user and LLM for calibration data extraction.

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | str | Unique identifier (prefix `conv`) |
| `created_at` | str | Creation timestamp (UTC) |
| `status` | Literal["active", "completed"] | Conversation state |
| `messages` | list[ConversationMessage] | Chat history |
| `draft_ids` | list[str] | Associated draft IDs |

**ConversationMessage:**
| Field | Type | Description |
|-------|------|-------------|
| `role` | Literal["user", "assistant", "system"] | Message sender |
| `content` | str | Message text |
| `timestamp` | str | Message timestamp |

### CalibrationDraft (`product/calibration_drafts/`)

A draft extracted by the LLM from conversation, pending user confirmation.

| Field | Type | Description |
|-------|------|-------------|
| `draft_id` | str | Unique identifier (prefix `cd`) |
| `source_type` | Literal["llm_calibration_draft"] | Always this value |
| `created_at` | str | Creation timestamp (UTC) |
| `conversation_id` | str | Parent conversation ID |
| `status` | Literal["pending", "confirmed", "rejected"] | Draft state |
| `behavior_metrics` | BehaviorMetricsExtract \| None | Extracted behavior data |
| `rubric_scores` | CalibrationScoreValues \| None | Extracted rubric scores |
| `external_evidence` | list[ExternalEvidenceExtract] | Extracted evidence items |
| `llm_model` | str \| None | LLM model used |
| `extraction_confidence` | Literal["high", "medium", "low"] | LLM's confidence |
| `llm_reasoning` | str | Why LLM extracted these values |
| `confirmed_at` | str \| None | Confirmation timestamp |
| `user_corrections` | dict[str, Any] | User corrections to extracted data |

**BehaviorMetricsExtract** — subset of WeeklyBehaviorMetricsRecord fields the LLM can extract (all optional except notes):
`week_start`, `week_end`, `branch_id`, `career_education_deep_work_minutes`, `planned_commitment_follow_through_rate`, `expense_logged_days`, `regular_sleep_nights`, `moderate_vigorous_activity_minutes`, `avoidable_health_risk_events`, `meaningful_social_contact_count`, `abandoned_committed_blocks`, `key_milestone_progress_pct`, `notes`.

**ExternalEvidenceExtract** — single evidence item extractable from conversation:
`domain`, `evidence_type`, `description`, `objective_strength`, `polarity`, `numeric_value`, `unit`.
