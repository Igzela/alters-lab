"""P6-M2 weekly review session runtime routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.weekly_review_session import (
    WeeklyReviewCompleteRequest,
    WeeklyReviewCompleteResponse,
    WeeklyReviewHealthResponse,
    WeeklyReviewListResponse,
    WeeklyReviewLoadResponse,
    WeeklyReviewStartRequest,
    WeeklyReviewStartResponse,
)
from alters_lab.services.weekly_review_session import (
    complete_weekly_review_session,
    list_weekly_review_sessions,
    load_weekly_review_session,
    save_weekly_review_session,
    start_weekly_review_session,
)

router = APIRouter(prefix="/weekly-review", tags=["weekly-review"])


@router.get("/health", response_model=WeeklyReviewHealthResponse)
def health():
    return WeeklyReviewHealthResponse()


@router.post("/start", response_model=WeeklyReviewStartResponse)
def start(body: WeeklyReviewStartRequest):
    try:
        session = start_weekly_review_session(body)
        path = save_weekly_review_session(session)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Weekly note not found: {body.weekly_note_record_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return WeeklyReviewStartResponse(status="started", session=session, session_path=str(path))


@router.get("/list", response_model=WeeklyReviewListResponse)
def list_sessions():
    sessions = list_weekly_review_sessions()
    return WeeklyReviewListResponse(sessions=sessions, count=len(sessions))


@router.get("/{session_id}", response_model=WeeklyReviewLoadResponse)
def load(session_id: str):
    try:
        return WeeklyReviewLoadResponse(session=load_weekly_review_session(session_id))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Weekly review session not found: {session_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{session_id}/complete", response_model=WeeklyReviewCompleteResponse)
def complete(session_id: str, body: WeeklyReviewCompleteRequest):
    try:
        session = load_weekly_review_session(session_id)
        completed = complete_weekly_review_session(session, body)
        path = save_weekly_review_session(completed)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Weekly review session not found: {session_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return WeeklyReviewCompleteResponse(status="completed", session=completed, session_path=str(path))
