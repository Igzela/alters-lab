"""P6-M6 weekly reminder and skip-with-reason schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class WeeklyReminderHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "weekly-reminder"
    provider_called: bool = False
    active_yaml_modified: bool = False


class WeeklyReminderRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reminder_id: str
    action: Literal["skipped", "completed"]
    reason: str | None = None
    weekly_review_session_id: str | None = None
    created_at: str
    counts_toward_usage_integrity: bool = True


class WeeklyReminderStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    fixed_weekly_reminder: bool = True
    skip_allowed: bool = True
    skip_requires_reason: bool = True
    last_record: WeeklyReminderRecord | None = None


class WeeklyReminderSkipRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    caller: str = "api"

    @field_validator("reason")
    @classmethod
    def reason_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("skip reason is required")
        return value.strip()


class WeeklyReminderCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weekly_review_session_id: str
    caller: str = "api"


class WeeklyReminderRecordResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    record: WeeklyReminderRecord
    record_path: str | None = None


class WeeklyReminderHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    records: list[WeeklyReminderRecord]
    count: int
