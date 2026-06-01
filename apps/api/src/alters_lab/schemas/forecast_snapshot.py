"""Forecast snapshot schema — locked forecast for future evaluation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alters_lab.services.p6_runtime import generate_record_id, utc_now


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
    route_a_summary: dict[str, Any] = Field(default_factory=dict)
    route_b_summary: dict[str, Any] = Field(default_factory=dict)
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
