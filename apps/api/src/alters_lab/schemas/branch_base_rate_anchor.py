"""Branch base-rate anchor schema — cautious Route A + Route B report."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DomainAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    route_a_direction: Literal["improving", "declining", "stable", "insufficient_data"]
    route_b_prior_direction: Literal["favorable", "unfavorable", "mixed", "unknown"]
    evidence_strength: Literal["weak", "moderate", "strong"]
    transfer_risk: Literal["low", "medium", "high"]
    explanation: str


class PriorSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_prior_direction: Literal["favorable", "unfavorable", "mixed", "unknown"]
    confidence: Literal["low", "medium", "high"]
    transfer_risk: Literal["low", "medium", "high"]
    explanation: str


class BranchBaseRateAnchorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: str
    profile_id: str | None = None
    lookback_weeks: int = Field(default=8, ge=2, le=52)


class BranchBaseRateAnchorResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: str
    generated_at: str
    route_a_available: bool
    route_b_available: bool
    population_percentile: float | None = None
    deviation_from_baseline: float | None = None
    prior_summary: PriorSummary
    domain_anchors: list[DomainAnchor]
    limitations: list[str] = Field(default_factory=list)
