"""P6-M10 behavior validation gate schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


BehaviorValidationOutcome = Literal[
    "P6_BEHAVIOR_VALIDATED",
    "P6_FAILED_TO_VALIDATE",
    "P6_USAGE_INVALID",
    "P6_INSUFFICIENT_DATA",
]


class UsageIntegrityAudit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weekly_notes_completed_honestly: bool
    calibration_records_created: bool
    primary_corrections_set: bool
    failure_reviews_honest: bool
    self_deception_risk_not_softened: bool
    sessions_not_skipped_too_often: bool


class BehaviorValidationMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_alignment_score_improves: bool
    repeated_negative_patterns_reduce: bool
    primary_correction_completion_rate_improves: bool


class BehaviorValidationEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weekly_review_ids: list[str] = Field(default_factory=list)
    calibration_record_ids: list[str] = Field(default_factory=list)
    pattern_review_ids: list[str] = Field(default_factory=list)
    metrics: BehaviorValidationMetrics
    usage_integrity: UsageIntegrityAudit
    save: bool = True
    caller: str = "api"


class BehaviorValidationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    validation_id: str
    outcome: BehaviorValidationOutcome
    status: str
    weekly_review_count: int
    calibration_record_count: int
    pattern_review_count: int
    metrics: BehaviorValidationMetrics
    usage_integrity: UsageIntegrityAudit
    usage_integrity_valid: bool
    behavior_improved: bool
    message: str
    created_at: str
    p6_sealed: bool = False
    active_yaml_modified: bool = False
    provider_called: bool = False


class BehaviorValidationHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "behavior-validation"
    seals_p6_directly: bool = False


class BehaviorValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    validation: BehaviorValidationRecord
    validation_path: str | None = None


class BehaviorValidationReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    validation: BehaviorValidationRecord | None = None
