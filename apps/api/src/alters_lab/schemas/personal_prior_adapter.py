"""Personal prior adapter schema — combines Route A, Route B, and external evidence."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceComponent(BaseModel):
    """A single evidence input to the adapter."""

    model_config = ConfigDict(extra="forbid")

    source: Literal[
        "route_a_behavior",
        "route_b_public_prior",
        "external_evidence",
        "outcome_target",
        "calibration_history",
        "contextual_prior",
    ]
    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    direction: Literal["improving", "declining", "stable", "mixed", "unknown"]
    strength: Literal["weak", "medium", "strong"]
    confidence: Literal["low", "medium", "high"]
    freshness_days: int | None = None
    explanation: str = ""
    limitations: list[str] = Field(default_factory=list)


class PersonalPriorAdapterResult(BaseModel):
    """Per-domain adapter result combining all evidence sources."""

    model_config = ConfigDict(extra="forbid")

    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    route_a_direction: Literal["improving", "declining", "stable", "mixed", "unknown", "insufficient_data"] = "unknown"
    route_b_direction: Literal["favorable", "unfavorable", "mixed", "unknown"] = "unknown"
    route_b_strength_level: Literal["strong_calibrated", "data_backed", "contextual", "unavailable"] = "unavailable"
    external_evidence_direction: Literal["improving", "declining", "stable", "mixed", "unknown"] = "unknown"
    alignment: Literal["aligned", "conflicted", "route_a_only", "route_b_only", "insufficient_data"] = "insufficient_data"
    conflict_level: Literal["none", "low", "medium", "high"] = "none"
    adjusted_forecast_direction: Literal["improving", "declining", "stable", "mixed", "unknown"] = "unknown"
    adjusted_confidence: Literal["low", "medium", "high"] = "low"
    confidence_drivers: list[str] = Field(default_factory=list)
    confidence_penalties: list[str] = Field(default_factory=list)
    next_evidence_to_collect: list[str] = Field(default_factory=list)
    explanation: str = ""


class PersonalPriorAdapterSummary(BaseModel):
    """Aggregate adapter result across all domains."""

    model_config = ConfigDict(extra="forbid")

    domain_results: list[PersonalPriorAdapterResult] = Field(default_factory=list)
    overall_alignment: Literal["aligned", "conflicted", "mixed", "insufficient_data"] = "insufficient_data"
    overall_conflict_level: Literal["none", "low", "medium", "high"] = "none"
    forecast_readiness: Literal["insufficient", "provisional", "usable", "strong"] = "insufficient"
    readiness_reasons: list[str] = Field(default_factory=list)
    readiness_blockers: list[str] = Field(default_factory=list)
    evidence_components: list[EvidenceComponent] = Field(default_factory=list)
