"""Pydantic schemas for trend analysis service."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TrendAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lookback_weeks: int = Field(default=8, ge=2, le=52)
    forecast_weeks: int = Field(default=4, ge=1, le=12)


class ForecastPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    week_offset: int = Field(ge=1, le=12)
    predicted_score: float = Field(ge=0.0, le=1.0)
    lower_bound: float = Field(ge=0.0, le=1.0)
    upper_bound: float = Field(ge=0.0, le=1.0)


class ConfidenceInterval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: Literal["low", "medium", "high"]
    data_count: int
    consistency_score: float = Field(ge=0.0, le=1.0)
    description: str


class TrendDimensionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: str
    direction: Literal["improving", "declining", "stable", "insufficient_data"]
    slope: float
    r_squared: float = Field(ge=0.0, le=1.0)
    confidence_level: Literal["low", "medium", "high"]
    data_points: int


class TrendAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    overall_direction: Literal["improving", "declining", "stable", "insufficient_data"]
    dimensions: list[TrendDimensionResult] = Field(default_factory=list)
    forecast: list[ForecastPoint] = Field(default_factory=list)
    confidence_interval: ConfidenceInterval
    generated_at: str


class TrendAnalysisHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "trend-analysis"
    mode: str = "evidence_only_read_only"
    provider_used: bool = False
    active_write_allowed: bool = False
    rubric_write_allowed: bool = False
