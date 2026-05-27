"""Routes for weekly review assistant mode."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.weekly_review_assistant import (
    WeeklyReviewAssistantHealthResponse,
    WeeklyReviewAssistantRequest,
    WeeklyReviewAssistantResponse,
    WeeklyReviewAssistantStatusResponse,
)
from alters_lab.services.weekly_review_assistant import (
    build_weekly_review_assistant_health,
    build_weekly_review_assistant_status,
    run_weekly_review_assistant,
)

router = APIRouter(prefix="/weekly-review-assistant", tags=["weekly-review-assistant"])


@router.get("/health", response_model=WeeklyReviewAssistantHealthResponse)
def health():
    return build_weekly_review_assistant_health()


@router.get("/status", response_model=WeeklyReviewAssistantStatusResponse)
def status():
    return build_weekly_review_assistant_status()


@router.post("/suggest", response_model=WeeklyReviewAssistantResponse)
def suggest(request: WeeklyReviewAssistantRequest):
    return run_weekly_review_assistant(request)
