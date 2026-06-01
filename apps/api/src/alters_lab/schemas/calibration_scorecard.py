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


class CalibrationScorecard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_evaluations: int = 0
    hit_count: int = 0
    miss_count: int = 0
    partial_count: int = 0
    unknown_count: int = 0
    by_domain: list[DomainScore] = Field(default_factory=list)
    signal_quality: SignalQuality = Field(default_factory=SignalQuality)
    calibration_confidence: Literal["low", "medium", "high"] = "low"
    limitations: list[str] = Field(default_factory=list)
