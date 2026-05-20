"""P6-M6 weekly reminder and skip-with-reason routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.weekly_reminder import (
    WeeklyReminderCompleteRequest,
    WeeklyReminderHealthResponse,
    WeeklyReminderHistoryResponse,
    WeeklyReminderRecordResponse,
    WeeklyReminderSkipRequest,
    WeeklyReminderStatusResponse,
)
from alters_lab.services.weekly_reminder import (
    build_complete_record,
    build_skip_record,
    latest_reminder_record,
    list_reminder_records,
    save_reminder_record,
)

router = APIRouter(prefix="/weekly-reminder", tags=["weekly-reminder"])


@router.get("/health", response_model=WeeklyReminderHealthResponse)
def health():
    return WeeklyReminderHealthResponse()


@router.get("/status", response_model=WeeklyReminderStatusResponse)
def status():
    return WeeklyReminderStatusResponse(last_record=latest_reminder_record())


@router.post("/skip", response_model=WeeklyReminderRecordResponse)
def skip(body: WeeklyReminderSkipRequest):
    record = build_skip_record(body)
    path = save_reminder_record(record)
    return WeeklyReminderRecordResponse(status="skipped", record=record, record_path=str(path))


@router.post("/complete", response_model=WeeklyReminderRecordResponse)
def complete(body: WeeklyReminderCompleteRequest):
    try:
        record = build_complete_record(body)
        path = save_reminder_record(record)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Weekly review session not found: {body.weekly_review_session_id}")
    return WeeklyReminderRecordResponse(status="completed", record=record, record_path=str(path))


@router.get("/history", response_model=WeeklyReminderHistoryResponse)
def history():
    records = list_reminder_records()
    return WeeklyReminderHistoryResponse(records=records, count=len(records))
