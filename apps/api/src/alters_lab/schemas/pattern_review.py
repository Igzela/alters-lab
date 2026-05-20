"""P6-M7 four-week pattern review schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PatternName = Literal[
    "repeated_noisy_progress",
    "repeated_avoidance_disguised_as_work",
    "repeated_sleep_breakdown",
    "repeated_over_scope",
    "repeated_action_mismatch",
    "repeated_primary_correction_failure",
]


class WeeklyPatternSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    week_id: str
    patterns: list[PatternName]
    confidence: float = Field(ge=0.0, le=1.0)


class PatternReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weekly_patterns: list[WeeklyPatternSignal]
    save: bool = True
    caller: str = "api"


class TriggeredPattern(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pattern: PatternName
    occurrences: int
    confidence: float
    strategy_constraint: str


class PatternReviewRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: str
    status: Literal["insufficient_data", "no_pattern", "pattern_triggered"]
    weeks_evaluated: int
    triggered_patterns: list[TriggeredPattern] = Field(default_factory=list)
    created_at: str
    active_yaml_modified: bool = False
    provider_called: bool = False


class PatternReviewHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "pattern-review"
    provider_called: bool = False
    active_yaml_modified: bool = False


class PatternReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    review: PatternReviewRecord
    review_path: str | None = None


class PatternReviewListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    reviews: list[PatternReviewRecord]
    count: int


class PatternReviewLoadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    review: PatternReviewRecord
