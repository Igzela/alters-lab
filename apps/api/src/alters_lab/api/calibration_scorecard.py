"""Calibration scorecard API routes."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.services.calibration_scorecard import build_scorecard

router = APIRouter(prefix="/forecast-scorecard", tags=["forecast-scorecard"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "calibration-scorecard",
        "provider_required": False,
    }


@router.get("/summary")
def summary():
    scorecard = build_scorecard()
    return {
        "status": "ok",
        "scorecard": scorecard.model_dump(),
    }
