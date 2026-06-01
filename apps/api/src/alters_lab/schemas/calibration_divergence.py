"""Calibration divergence schema — dual-track subjective vs objective comparison."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CalibrationDivergenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: str | None = None
    lookback_weeks: int = Field(default=8, ge=2, le=52)


class SubjectiveTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_alignment_direction: Literal["improving", "declining", "stable", "insufficient_data"]
    data_points: int


class ObjectiveTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    behavior_direction: Literal["improving", "declining", "stable", "mixed", "insufficient_data"]
    milestone_direction: Literal["improving", "declining", "stable", "insufficient_data"]
    data_points: int


class DivergenceFlag(BaseModel):
    model_config = ConfigDict(extra="forbid")

    flag_id: str
    severity: Literal["info", "warn", "critical"]
    explanation: str
    suggested_calibration_question: str


class CalibrationDivergenceResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    generated_at: str
    subjective_track: SubjectiveTrack
    objective_track: ObjectiveTrack
    divergence_status: Literal[
        "converging",
        "diverging_positive_subjective",
        "diverging_negative_subjective",
        "mixed",
        "insufficient_data",
    ]
    flags: list[DivergenceFlag] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
