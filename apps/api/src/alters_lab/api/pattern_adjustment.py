"""Pattern adjustment API router."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.pattern_adjustment import (
    PatternAdjustmentHealthResponse,
    PatternAdjustmentRequest,
    PatternAdjustmentResult,
)
from alters_lab.services.pattern_adjustment import adjust_forecast
from alters_lab.services.calibration_loop import get_repo_root

router = APIRouter(prefix="/pattern-adjustment", tags=["pattern-adjustment"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=PatternAdjustmentHealthResponse)
def health():
    return PatternAdjustmentHealthResponse()


@router.post("/adjust", response_model=PatternAdjustmentResult)
def adjust(request: PatternAdjustmentRequest):
    try:
        return adjust_forecast(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
