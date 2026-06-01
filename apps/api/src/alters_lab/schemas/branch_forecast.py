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


class CalibrationDivergenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    divergence_status: str
    flags: list[dict]


class OutcomeTargetSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active_targets: int
    achieved_targets: int
    missed_targets: int


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
    limitations: list[str] = Field(default_factory=list)
    next_evidence_to_collect: list[str] = Field(default_factory=list)
