"""P6-M2 weekly review session runtime service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.weekly_review_session import (
    WeeklyReviewCompleteRequest,
    WeeklyReviewSessionRecord,
    WeeklyReviewStartRequest,
)
from alters_lab.services.obsidian_weekly_note import load_weekly_note_record
from alters_lab.services.p6_runtime import generate_record_id, list_records, read_record, utc_now, write_record

VALID_ALTER_IDS = {"alter_A", "alter_B", "alter_C", "alter_D"}


def start_weekly_review_session(
    request: WeeklyReviewStartRequest,
    repo_root: Path | None = None,
) -> WeeklyReviewSessionRecord:
    note = load_weekly_note_record(request.weekly_note_record_id, repo_root)
    if request.selected_alter_id is not None and request.selected_alter_id not in VALID_ALTER_IDS:
        raise ValueError(f"Invalid selected_alter_id: {request.selected_alter_id}")
    return WeeklyReviewSessionRecord(
        session_id=generate_record_id("weekly_review"),
        weekly_note_record_id=note.record_id,
        session_type=note.session_type,
        status="started",
        selected_alter_id=request.selected_alter_id,
        created_at=utc_now(),
    )


def save_weekly_review_session(record: WeeklyReviewSessionRecord, repo_root: Path | None = None) -> Path:
    return write_record("weekly_reviews", record.session_id, record.model_dump(), repo_root)


def load_weekly_review_session(session_id: str, repo_root: Path | None = None) -> WeeklyReviewSessionRecord:
    return WeeklyReviewSessionRecord(**read_record("weekly_reviews", session_id, repo_root))


def list_weekly_review_sessions(repo_root: Path | None = None) -> list[WeeklyReviewSessionRecord]:
    return [WeeklyReviewSessionRecord(**r) for r in list_records("weekly_reviews", repo_root)]


def complete_weekly_review_session(
    session: WeeklyReviewSessionRecord,
    request: WeeklyReviewCompleteRequest,
) -> WeeklyReviewSessionRecord:
    updated = session.model_copy(deep=True)
    updated.status = "completed"
    updated.review_note = request.review_note
    updated.dialogue_summary = request.dialogue_summary
    updated.next_week_primary_correction = request.primary_next_correction
    updated.supporting_actions = request.supporting_actions
    updated.calibration_record_shell = {
        "record_type": "weekly_review_calibration_shell",
        "derived_from_raw_note": True,
        "weekly_note_record_id": session.weekly_note_record_id,
        "weekly_review_session_id": session.session_id,
        "scoring_pending": True,
        **request.calibration_record_shell,
    }
    updated.completed_at = utc_now()
    return updated
