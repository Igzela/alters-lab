"""Branch forecast schema — user-facing prediction report separating evidence types."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BranchForecastRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: str
    profile_id: str | None = None
    lookback_weeks: int = Field(default=8, ge=2, le=52)
    horizon_months: int = Field(default=3, ge=1, le=24)


class ForecastSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trajectory_direction: Literal["improving", "declining", "stable", "mixed", "unknown"]
    confidence: Literal["low", "medium", "high"]
    credibility: Literal["low", "medium", "high"]
    explanation: str


class RouteAPersonalEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    available: bool
    behavior_trends_summary: str
    milestone_progress_summary: str
    action_alignment_summary: str


class RouteBPopulationPrior(BaseModel):
    model_config = ConfigDict(extra="forbid")

    available: bool
    prior_direction: Literal["favorable", "unfavorable", "mixed", "unknown"]
    transfer_risk: Literal["low", "medium", "high"]
    evidence_strength: Literal["weak", "moderate", "strong"]
    population_percentile: float | None = None
    deviation_from_baseline: float | None = None
    explanation: str
    artifact_ids: list[str] = Field(default_factory=list)
    model_card_ids: list[str] = Field(default_factory=list)
    dataset_source_ids: list[str] = Field(default_factory=list)
    approved_artifact_count: int = 0
    artifact_class: Literal[
        "contextual_prior", "data_backed_baseline", "calibrated_model", "mixed", "none"
    ] = "none"
    contextual_prior_ids: list[str] = Field(default_factory=list)


class CalibrationDivergenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    divergence_status: str
    flags: list[dict]


class OutcomeTargetSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active_targets: int
    achieved_targets: int
    missed_targets: int


class DomainForecastPrediction(BaseModel):
    """Per-domain forecast prediction with evidence source tracking."""

    model_config = ConfigDict(extra="forbid")

    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    route_a_direction: Literal["improving", "declining", "stable", "insufficient_data", "unknown"] = "unknown"
    route_b_prior_direction: Literal["favorable", "unfavorable", "mixed", "unknown"] = "unknown"
    predicted_direction: Literal["improving", "declining", "stable", "mixed", "unknown"] = "unknown"
    predicted_direction_source: Literal["route_a", "route_b", "behavior_metric", "outcome_target", "overall_fallback", "unknown"] = "unknown"
    confidence: Literal["low", "medium", "high"] = "low"
    evidence_strength: Literal["weak", "moderate", "strong"] = "weak"
    transfer_risk: Literal["low", "medium", "high"] = "high"
    explanation: str = ""
    artifact_id: str | None = None
    model_card_id: str | None = None
    dataset_source_id: str | None = None
    approved_for_route_b: bool = False
    artifact_class: Literal[
        "contextual_prior", "data_backed_baseline", "calibrated_model", "none"
    ] = "none"


class BranchForecastResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: str
    generated_at: str
    horizon_months: int
    forecast_summary: ForecastSummary
    route_a_personal_evidence: RouteAPersonalEvidence
    route_b_population_prior: RouteBPopulationPrior
    calibration_divergence: CalibrationDivergenceSummary
    outcome_targets: OutcomeTargetSummary
    domain_predictions: list[DomainForecastPrediction] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    next_evidence_to_collect: list[str] = Field(default_factory=list)
