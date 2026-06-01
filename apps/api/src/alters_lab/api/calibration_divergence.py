"""Calibration divergence API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.calibration_divergence import CalibrationDivergenceRequest
from alters_lab.services.calibration_divergence import analyze_calibration_divergence

router = APIRouter(prefix="/divergence-analysis", tags=["divergence-analysis"])


@router.post("/analyze")
def analyze(body: CalibrationDivergenceRequest):
    try:
        result = analyze_calibration_divergence(body)
        return result.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
