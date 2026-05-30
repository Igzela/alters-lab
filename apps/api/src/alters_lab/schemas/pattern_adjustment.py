"""Pydantic schemas for pattern-adjusted forecast."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from alters_lab.schemas.trend_analysis import ForecastPoint


class PatternAdjustmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lookback_weeks: int = Field(default=8, ge=2, le=52)
    forecast_weeks: int = Field(default=4, ge=1, le=12)


class AdjustedForecastPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    week_offset: int = Field(ge=1, le=12)
    original_score: float = Field(ge=0.0, le=1.0)
    adjusted_score: float = Field(ge=0.0, le=1.0)
    adjustment_delta: float
    adjustment_reason: str
    lower_bound: float = Field(ge=0.0, le=1.0)
    upper_bound: float = Field(ge=0.0, le=1.0)


class PatternAdjustmentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    has_patterns: bool
    original_forecast: list[ForecastPoint]
    adjusted_forecast: list[AdjustedForecastPoint]
    adjustments_applied: list[str] = Field(default_factory=list)
    generated_at: str


class PatternAdjustmentHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "pattern-adjustment"
    mode: str = "evidence_only_read_only"
    provider_used: bool = False
    active_write_allowed: bool = False
    rubric_write_allowed: bool = False
