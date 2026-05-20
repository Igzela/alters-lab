"""P6-M2 weekly review session runtime schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from alters_lab.schemas.obsidian_weekly_note import SessionType


class WeeklyReviewBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    derived_from_weekly_note: bool = True
    active_yaml_modified: bool = False
    rubric_modified: bool = False
    provider_called: bool = False
    score_auto_generated: bool = False
    archive_triggered: bool = False
    checkpoint_triggered: bool = False


class WeeklyReviewStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weekly_note_record_id: str
    selected_alter_id: str | None = None
    caller: str = "api"


class WeeklyReviewCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_note: str
    dialogue_summary: str = ""
    primary_next_correction: str
    supporting_actions: list[str] = Field(default_factory=list, max_length=2)
    calibration_record_shell: dict = Field(default_factory=dict)
    caller: str = "api"

    @field_validator("review_note", "primary_next_correction")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be blank")
        return value.strip()


class WeeklyReviewSessionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    weekly_note_record_id: str
    session_type: SessionType
    status: Literal["started", "completed"]
    selected_alter_id: str | None = None
    dialogue_summary: str = ""
    review_note: str | None = None
    calibration_record_shell: dict = Field(default_factory=dict)
    next_week_primary_correction: str | None = None
    supporting_actions: list[str] = Field(default_factory=list, max_length=2)
    created_at: str
    completed_at: str | None = None
    boundary_confirmations: WeeklyReviewBoundaryConfirmations = Field(
        default_factory=WeeklyReviewBoundaryConfirmations
    )


class WeeklyReviewHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "weekly-review"
    provider_called: bool = False
    active_yaml_modified: bool = False


class WeeklyReviewStartResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    session: WeeklyReviewSessionRecord
    session_path: str | None = None


class WeeklyReviewCompleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    session: WeeklyReviewSessionRecord
    session_path: str | None = None


class WeeklyReviewListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    sessions: list[WeeklyReviewSessionRecord]
    count: int


class WeeklyReviewLoadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    session: WeeklyReviewSessionRecord
