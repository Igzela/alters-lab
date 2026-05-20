"""Pydantic schemas for P4-M5 Rubric Delta Suggestion."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RubricDeltaBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestion_only: bool = True
    rubric_modified: bool = False
    active_yaml_modified: bool = False
    provider_used: bool = False
    frontend_added: bool = False
    database_added: bool = False
    archive_created: bool = False
    regeneration_triggered: bool = False
    human_confirmation_required: bool = True


class RubricDeltaDimensionSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: str
    mismatch_count: int
    average_drift: float
    direction: Literal[
        "actual_lower_than_expected",
        "actual_higher_than_expected",
        "mixed",
    ]
    suggestion: str
    severity: Literal["low", "medium", "high"]


class RubricDeltaSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    status: str = "pending_review"
    source: str = "calibration_history"
    dimensions: list[RubricDeltaDimensionSuggestion]
    summary: str
    evidence_refs: list[str]
    rubric_write_allowed: bool = False
    human_confirmation_required: bool = True
    created_at: str
    boundary_confirmations: RubricDeltaBoundaryConfirmations

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value != "pending_review":
            raise ValueError("status must be pending_review")
        return value

    @field_validator("rubric_write_allowed")
    @classmethod
    def validate_rubric_write_allowed(cls, value: bool) -> bool:
        if value is not False:
            raise ValueError("rubric_write_allowed must be false")
        return value

    @field_validator("human_confirmation_required")
    @classmethod
    def validate_human_confirmation_required(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("human_confirmation_required must be true")
        return value


class RubricDeltaSuggestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_records: int = Field(default=2, ge=1)
    drift_threshold: float = Field(default=0.25, ge=0, le=1)
    save_suggestion: bool = False
    caller: str = "api"


class RubricDeltaSuggestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["suggested", "insufficient_data", "saved", "rejected"]
    suggestion: RubricDeltaSuggestion | None
    suggestion_path: str | None
    boundary_confirmations: dict


class RubricDeltaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    suggestions: list[dict]
    count: int
    boundary_confirmations: dict


class RubricDeltaHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "rubric-delta"
    mode: str = "suggestion_only_no_rubric_write"
    provider_used: bool = False
    active_write_allowed: bool = False
    rubric_write_allowed: bool = False
