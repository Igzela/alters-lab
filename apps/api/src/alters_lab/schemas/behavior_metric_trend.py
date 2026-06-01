"""Behavior metric trend schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BehaviorMetricTrendResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric_id: str
    direction: Literal["improving", "declining", "stable", "insufficient_data"]
    slope: float
    confidence_level: Literal["low", "medium", "high"]
    data_points: int

    current_value: float | int | None = None
    rolling_4w_median: float | None = None

    # Route B placeholders — do not populate until population prior layer exists.
    population_percentile: float | None = Field(default=None, ge=0.0, le=100.0)
    deviation_from_baseline: float | None = None
    route_a_available: bool = True
    route_b_available: bool = False


class BehaviorMetricTrendResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    lookback_weeks: int
    trends: list[BehaviorMetricTrendResult]
    generated_at: str


class BehaviorMetricTrendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lookback_weeks: int = Field(default=8, ge=2, le=52)
