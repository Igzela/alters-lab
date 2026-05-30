"""Trend analysis API router."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.trend_analysis import (
    TrendAnalysisHealthResponse,
    TrendAnalysisRequest,
    TrendAnalysisResult,
)
from alters_lab.services.trend_analysis import analyze_trend
from alters_lab.services.calibration_loop import get_repo_root

router = APIRouter(prefix="/trend-analysis", tags=["trend-analysis"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=TrendAnalysisHealthResponse)
def health():
    return TrendAnalysisHealthResponse()


@router.post("/analyze", response_model=TrendAnalysisResult)
def run_analysis(request: TrendAnalysisRequest):
    try:
        return analyze_trend(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
