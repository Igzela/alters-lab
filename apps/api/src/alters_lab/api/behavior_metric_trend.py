"""Behavior metric trend API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.behavior_metric_trend import BehaviorMetricTrendRequest
from alters_lab.services.behavior_metric_trend import analyze_behavior_trends

router = APIRouter(prefix="/behavior-metric-trend", tags=["behavior-metric-trend"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "behavior-metric-trend",
        "provider_required": False,
    }


@router.post("/analyze")
def analyze(body: BehaviorMetricTrendRequest):
    try:
        result = analyze_behavior_trends(body)
        return result.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
