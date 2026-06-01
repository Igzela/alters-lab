"""Phase 12 pilot schemas — source selection, baseline artifacts for the dual-source pilot."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Source Selection ---

class SourceSelectionEntry(BaseModel):
    """A single source selection decision in the dual-source pilot."""

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
    primary_domains: list[str] = Field(default_factory=list)
    expected_strengths: list[str] = Field(default_factory=list)
    transfer_risk: Literal["low", "medium", "high"]
    known_limitations: list[str] = Field(default_factory=list)
    first_pass_decision: Literal["include", "defer", "reject"]
    rationale: str = ""


class PopulationBaselineSourceSelection(BaseModel):
    """Complete source selection for Phase 12 dual-source pilot."""

    model_config = ConfigDict(extra="forbid")

    version: str = "0.1"
    sources: list[SourceSelectionEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_decisions(self) -> PopulationBaselineSourceSelection:
        """Enforce source selection invariants."""
        included = [s for s in self.sources if s.first_pass_decision == "include"]
        if len(included) < 1:
            raise ValueError("At least one source must be included")
        return self


# --- Baseline Outcome Candidate ---

class BaselineOutcomeCandidate(BaseModel):
    """A candidate outcome for the population baseline pilot."""

    model_config = ConfigDict(extra="forbid")

    outcome_id: str
    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    label: str
    dataset_source_id: str
    operational_definition: str
    measurement_type: Literal["binary", "ordinal", "continuous", "survival", "categorical"]
    time_horizon_months: int | None = None
    target_direction: Literal["higher_is_better", "lower_is_better", "category_dependent"]
    expected_missingness_risk: Literal["low", "medium", "high"]
    transfer_risk: Literal["low", "medium", "high"]
    first_pass_status: Literal["candidate", "preferred", "rejected"]
    limitations: list[str] = Field(default_factory=list)


# --- Baseline Feature Candidate ---

class BaselineFeatureCandidate(BaseModel):
    """A candidate feature mapping for the population baseline pilot."""

    model_config = ConfigDict(extra="forbid")

    feature_id: str
    construct_id: str
    dataset_source_id: str
    source_variable_candidates: list[str] = Field(default_factory=list)
    maps_to_predictor_profile_fields: list[str] = Field(default_factory=list)
    maps_to_behavior_metric_ids: list[str] = Field(default_factory=list)
    expected_direction: Literal["positive", "negative", "mixed", "unknown"]
    transformation_notes: str = ""
    missingness_notes: str = ""
    transfer_risk: Literal["low", "medium", "high"]
    first_pass_status: Literal["candidate", "preferred", "rejected"]


# --- Baseline Table Artifact ---

class BaselineTableArtifact(BaseModel):
    """Descriptive population statistics before any ML model is trained."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    dataset_source_id: str
    outcome_id: str
    subgroup_definition: str
    n: int
    observed_rate_or_mean: float
    confidence_interval: str
    missingness_rate: float
    transfer_risk: Literal["low", "medium", "high"]
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _enforce_safety(self) -> BaselineTableArtifact:
        """Enforce baseline table safety constraints."""
        if self.n < 1:
            raise ValueError("Sample size must be positive")
        if not (0.0 <= self.missingness_rate <= 1.0):
            raise ValueError("missingness_rate must be between 0 and 1")
        return self
