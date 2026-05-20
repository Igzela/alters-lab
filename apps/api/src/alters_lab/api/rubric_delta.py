"""Rubric Delta Suggestion API for P4-M5."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.rubric_delta import (
    RubricDeltaHealthResponse,
    RubricDeltaListResponse,
    RubricDeltaSuggestRequest,
    RubricDeltaSuggestResponse,
)
from alters_lab.services.calibration_loop import get_repo_root
from alters_lab.services.rubric_delta import (
    list_rubric_delta_suggestions,
    rubric_delta_boundary_confirmations,
    suggest_rubric_delta,
)

router = APIRouter(prefix="/rubric-delta", tags=["rubric-delta"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=RubricDeltaHealthResponse)
def health():
    return RubricDeltaHealthResponse()


@router.post("/suggest", response_model=RubricDeltaSuggestResponse)
def suggest(request: RubricDeltaSuggestRequest):
    try:
        status, suggestion, path = suggest_rubric_delta(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RubricDeltaSuggestResponse(
        status=status,  # type: ignore[arg-type]
        suggestion=suggestion,
        suggestion_path=str(path) if path else None,
        boundary_confirmations=rubric_delta_boundary_confirmations(),
    )


@router.get("/list", response_model=RubricDeltaListResponse)
def list_suggestions():
    suggestions = list_rubric_delta_suggestions(_repo_root())
    return RubricDeltaListResponse(
        status="ok",
        suggestions=suggestions,
        count=len(suggestions),
        boundary_confirmations=rubric_delta_boundary_confirmations(),
    )
