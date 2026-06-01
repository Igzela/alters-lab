"""Forecast evaluation schema — compare predictions against observed evidence."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alters_lab.services.p6_runtime import generate_record_id, utc_now


class DomainResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    predicted_direction: Literal["improving", "declining", "stable", "mixed", "unknown"]
    observed_direction: Literal["improved", "declined", "stable", "mixed", "unknown"]
    match_result: Literal["hit", "miss", "partial", "unknown"]
    evidence_strength: Literal["weak", "moderate", "strong"] = "weak"
    explanation: str = ""


class ForecastEvaluationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluation_id: str
    source_type: Literal["forecast_evaluation"] = "forecast_evaluation"
    snapshot_id: str
    branch_id: str
    evaluated_at: str
    evaluation_horizon_elapsed: bool = False
    evidence_ids: list[str] = Field(default_factory=list)
    domain_results: list[DomainResult] = Field(default_factory=list)
    overall_result: Literal["hit", "miss", "partial", "unknown"] = "unknown"
    calibration_notes: list[str] = Field(default_factory=list)
    misleading_signals: list[str] = Field(default_factory=list)
    predictive_signals: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def auto_fill_ids(cls, data: dict) -> dict:
        if not data.get("evaluation_id"):
            data["evaluation_id"] = generate_record_id("fe")
        if not data.get("evaluated_at"):
            data["evaluated_at"] = utc_now()
        return data
