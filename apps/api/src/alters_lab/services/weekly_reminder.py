"""P6-M6 weekly reminder and skip-with-reason service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.weekly_reminder import (
    WeeklyReminderCompleteRequest,
    WeeklyReminderRecord,
    WeeklyReminderSkipRequest,
)
from alters_lab.services.p6_runtime import generate_record_id, list_records, utc_now, write_record
from alters_lab.services.weekly_review_session import load_weekly_review_session


def build_skip_record(request: WeeklyReminderSkipRequest) -> WeeklyReminderRecord:
    return WeeklyReminderRecord(
        reminder_id=generate_record_id("weekly_reminder"),
        action="skipped",
        reason=request.reason,
        created_at=utc_now(),
    )


def build_complete_record(
    request: WeeklyReminderCompleteRequest,
    repo_root: Path | None = None,
) -> WeeklyReminderRecord:
    load_weekly_review_session(request.weekly_review_session_id, repo_root)
    return WeeklyReminderRecord(
        reminder_id=generate_record_id("weekly_reminder"),
        action="completed",
        weekly_review_session_id=request.weekly_review_session_id,
        created_at=utc_now(),
    )


def save_reminder_record(record: WeeklyReminderRecord, repo_root: Path | None = None) -> Path:
    return write_record("reminders", record.reminder_id, record.model_dump(), repo_root)


def list_reminder_records(repo_root: Path | None = None) -> list[WeeklyReminderRecord]:
    return [WeeklyReminderRecord(**r) for r in list_records("reminders", repo_root)]


def latest_reminder_record(repo_root: Path | None = None) -> WeeklyReminderRecord | None:
    records = list_reminder_records(repo_root)
    return records[-1] if records else None
