"""Forecast snapshot schema — locked forecast for future evaluation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alters_lab.services.p6_runtime import generate_record_id, utc_now


class DomainPrediction(BaseModel):
    """Per-domain predicted direction extracted from forecast data."""

    model_config = ConfigDict(extra="forbid")

    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    predicted_direction: Literal["improving", "declining", "stable", "mixed", "unknown"]
    source: Literal["route_a", "route_b", "behavior_metric", "outcome_target", "overall_fallback", "adapter", "unknown"] = "unknown"
    confidence: Literal["low", "medium", "high"] = "low"
    explanation: str = ""
    route_a_direction: Literal["improving", "declining", "stable", "insufficient_data", "unknown"] = "unknown"
    route_b_prior_direction: Literal["favorable", "unfavorable", "mixed", "unknown"] = "unknown"
    evidence_strength: Literal["weak", "moderate", "strong"] = "weak"
    transfer_risk: Literal["low", "medium", "high"] = "high"
    artifact_id: str | None = None
    model_card_id: str | None = None
    dataset_source_id: str | None = None
    approved_for_route_b: bool = False
    artifact_class: Literal["contextual_prior", "data_backed_baseline", "calibrated_model", "none"] = "none"
    strength_level: Literal["strong_calibrated", "data_backed", "contextual", "none"] = "none"
    adapter_adjusted_direction: Literal["improving", "declining", "stable", "mixed", "unknown"] | None = None
    adapter_conflict_level: Literal["none", "low", "medium", "high"] | None = None
    adapter_alignment: Literal["aligned", "conflicted", "route_a_only", "route_b_only", "insufficient_data"] | None = None


class ForecastSummarySnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trajectory_direction: Literal["improving", "declining", "stable", "mixed", "unknown"]
    confidence: Literal["low", "medium", "high"]
    credibility: Literal["low", "medium", "high"]
    explanation: str


class ForecastSnapshotRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_id: str
    source_type: Literal["forecast_snapshot"] = "forecast_snapshot"
    branch_id: str
    created_at: str
    horizon_months: int = Field(ge=1, le=24)
    forecast_payload: dict[str, Any] = Field(default_factory=dict)
    forecast_summary: ForecastSummarySnapshot
    domain_predictions: list[DomainPrediction] = Field(default_factory=list)
    route_a_summary: dict[str, Any] = Field(default_factory=dict)
    route_b_summary: dict[str, Any] = Field(default_factory=dict)
    adapter_summary: dict[str, Any] = Field(default_factory=dict)
    calibration_divergence_summary: dict[str, Any] = Field(default_factory=dict)
    outcome_target_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    locked: bool = True

    @model_validator(mode="before")
    @classmethod
    def auto_fill_ids(cls, data: dict) -> dict:
        if not data.get("snapshot_id"):
            data["snapshot_id"] = generate_record_id("fs")
        if not data.get("created_at"):
            data["created_at"] = utc_now()
        return data
