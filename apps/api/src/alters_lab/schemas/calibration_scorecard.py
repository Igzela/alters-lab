"""Calibration scorecard schema — aggregate forecast evaluation statistics."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DomainScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: str
    hit_rate: float | None = None
    evidence_strength_distribution: dict[str, int] = Field(default_factory=dict)


class SignalQuality(BaseModel):
    model_config = ConfigDict(extra="forbid")

    predictive_signals: list[str] = Field(default_factory=list)
    misleading_signals: list[str] = Field(default_factory=list)


class SourceHitRates(BaseModel):
    """Hit rates broken down by prediction source (Route A, Route B, Adapter)."""

    model_config = ConfigDict(extra="forbid")

    route_a_hit_count: int = 0
    route_a_miss_count: int = 0
    route_a_partial_count: int = 0
    route_a_unknown_count: int = 0
    route_b_hit_count: int = 0
    route_b_miss_count: int = 0
    route_b_partial_count: int = 0
    route_b_unknown_count: int = 0
    adapter_hit_count: int = 0
    adapter_miss_count: int = 0
    adapter_partial_count: int = 0
    adapter_unknown_count: int = 0
    conflict_outcomes: dict[str, int] = Field(default_factory=dict)


class CalibrationScorecard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_evaluations: int = 0
    hit_count: int = 0
    miss_count: int = 0
    partial_count: int = 0
    unknown_count: int = 0
    by_domain: list[DomainScore] = Field(default_factory=list)
    signal_quality: SignalQuality = Field(default_factory=SignalQuality)
    source_hit_rates: SourceHitRates = Field(default_factory=SourceHitRates)
    calibration_confidence: Literal["low", "medium", "high"] = "low"
    limitations: list[str] = Field(default_factory=list)
