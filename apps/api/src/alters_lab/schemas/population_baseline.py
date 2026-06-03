"""Population baseline schemas for public-prior integration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Shared domain enum (matches existing 5-domain system) ---

Domain = Literal[
    "career_education",
    "financial",
    "health",
    "relationship",
    "subjective_wellbeing",
]


# --- Sub-models ---

class CalibrationMetrics(BaseModel):
    """Calibration metrics for a population baseline model."""

    model_config = ConfigDict(extra="forbid")

    brier_score: float | None = None
    calibration_slope: float | None = None
    calibration_intercept: float | None = None
    auc: float | None = None
    r2: float | None = None


# --- Top-level models ---


class PublicDatasetSource(BaseModel):
    """A public dataset or literature source used for population baselines."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    label: str
    source_type: Literal[
        "longitudinal_dataset",
        "panel_dataset",
        "benchmark_dataset",
        "literature_review",
        "meta_analysis",
    ]
    access_url: str | None = None
    access_notes: str = ""
    population_description: str
    time_horizon: str
    available_domains: list[Domain] = Field(default_factory=list)
    transfer_risk: Literal["low", "medium", "high"]
    allowed_use: Literal["research_only", "prior_generation", "documentation_only"]
    notes: str = ""


class PublicOutcomeDefinition(BaseModel):
    """An externally defined outcome used to evaluate forecasts."""

    model_config = ConfigDict(extra="forbid")

    outcome_id: str
    domain: Domain
    label: str
    definition: str
    time_horizon_months: int | None = None
    measurement_type: Literal[
        "binary", "ordinal", "continuous", "survival", "categorical"
    ]
    dataset_source_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class PublicFeatureMapping(BaseModel):
    """Maps public dataset variables to internal predictor/behavior fields."""

    model_config = ConfigDict(extra="forbid")

    feature_id: str
    construct_id: str
    label: str
    source_variable_names: list[str] = Field(default_factory=list)
    maps_to_predictor_profile_fields: list[str] = Field(default_factory=list)
    maps_to_behavior_metric_ids: list[str] = Field(default_factory=list)
    expected_direction: Literal["positive", "negative", "mixed", "unknown"]
    transformation_notes: str = ""
    missingness_notes: str = ""
    transfer_risk: Literal["low", "medium", "high"]


class PopulationBaselineModelCard(BaseModel):
    """Model card for a population baseline model artifact."""

    model_config = ConfigDict(extra="forbid")

    model_id: str
    source_dataset_ids: list[str] = Field(default_factory=list)
    outcome_id: str
    feature_mapping_ids: list[str] = Field(default_factory=list)
    model_family: Literal[
        "logistic_regression",
        "elastic_net",
        "ordinal_regression",
        "survival_model",
        "baseline_table",
        "literature_prior_only",
    ]
    training_status: Literal["not_trained", "trained", "validated", "rejected"] = (
        "not_trained"
    )
    evaluation_summary: str = ""
    calibration_metrics: CalibrationMetrics = Field(default_factory=CalibrationMetrics)
    transfer_risk: Literal["low", "medium", "high"]
    approved_for_route_b: bool = False
    limitations: list[str] = Field(default_factory=list)
    artifact_class: Literal[
        "contextual_prior", "data_backed_baseline", "calibrated_model"
    ] = "contextual_prior"
    approval_level: Literal["unapproved", "lab_only", "route_b_approved"] = (
        "unapproved"
    )
    approval_reason: str = ""
    approval_blockers: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _enforce_approval_guardrails(self) -> PopulationBaselineModelCard:
        """Enforce approval-level consistency rules."""
        # Sync approved_for_route_b with approval_level
        if self.approval_level == "route_b_approved":
            object.__setattr__(self, "approved_for_route_b", True)
        elif self.approval_level in ("unapproved", "lab_only"):
            object.__setattr__(self, "approved_for_route_b", False)

        # Contextual priors cannot be route_b_approved
        if (
            self.artifact_class == "contextual_prior"
            and self.approval_level == "route_b_approved"
        ):
            raise ValueError(
                "contextual_prior cannot be route_b_approved. "
                "Upgrade to data_backed_baseline or calibrated_model first."
            )

        # Route B approval requires empty blockers
        if (
            self.approval_level == "route_b_approved"
            and self.approval_blockers
        ):
            raise ValueError(
                f"Cannot approve for Route B with blockers: {self.approval_blockers}"
            )

        return self


class PopulationPriorArtifact(BaseModel):
    """A prior derived from a population baseline model, ready for display."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    model_id: str
    generated_at: str
    domain: Domain
    prior_type: Literal["textual", "probability_band", "percentile", "baseline_table"]
    prior_direction: Literal["favorable", "unfavorable", "mixed", "unknown"]
    probability_band: str | None = None
    population_percentile: float | None = None
    deviation_from_baseline: float | None = None
    confidence: Literal["low", "medium", "high"]
    transfer_risk: Literal["low", "medium", "high"]
    explanation: str
    limitations: list[str] = Field(default_factory=list)
    artifact_class: Literal[
        "contextual_prior", "data_backed_baseline", "calibrated_model"
    ] = "contextual_prior"
    actual_data_used: bool = False
    baseline_table_id: str | None = None
    value_labels_confirmed: bool = False
    missingness_reviewed: bool = False
    validation_report_id: str | None = None

    @model_validator(mode="after")
    def _enforce_guardrails(self) -> PopulationPriorArtifact:
        """Enforce guardrails on artifact classes and confidence caps."""
        # High transfer risk caps confidence at low or medium
        if self.transfer_risk == "high" and self.confidence == "high":
            object.__setattr__(self, "confidence", "medium")

        # Contextual priors without actual data cannot claim data-backed status
        if (
            self.artifact_class == "contextual_prior"
            and self.actual_data_used
        ):
            raise ValueError(
                "contextual_prior cannot have actual_data_used=true. "
                "Use data_backed_baseline or calibrated_model."
            )

        # Data-backed baselines must have actual data
        if (
            self.artifact_class == "data_backed_baseline"
            and not self.actual_data_used
        ):
            raise ValueError(
                "data_backed_baseline must have actual_data_used=true."
            )

        return self
