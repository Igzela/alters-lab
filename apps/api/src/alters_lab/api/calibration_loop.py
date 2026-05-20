"""Calibration loop API for P4-M2/M3/M4."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.calibration_loop import (
    CalibrationHistoryResponse,
    CalibrationLoopHealthResponse,
    DriftCalculationRequest,
    DriftCalculationResult,
    RealityScoreRequest,
    RealityScoreResponse,
)
from alters_lab.services.calibration_loop import (
    build_calibration_history,
    calculate_drift,
    calibration_boundary_confirmations,
    get_repo_root,
    submit_reality_score,
)

router = APIRouter(prefix="/calibration-loop", tags=["calibration-loop"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=CalibrationLoopHealthResponse)
def health():
    return CalibrationLoopHealthResponse()


@router.post("/reality-scores", response_model=RealityScoreResponse)
def submit_score(request: RealityScoreRequest):
    try:
        status, record, path = submit_reality_score(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RealityScoreResponse(
        status=status,
        record=record,
        score_path=str(path),
        boundary_confirmations=calibration_boundary_confirmations(),
    )


@router.post("/drift/calculate", response_model=DriftCalculationResult)
def calculate_drift_evidence(request: DriftCalculationRequest):
    return calculate_drift(request)


@router.get("/history", response_model=CalibrationHistoryResponse)
def history():
    try:
        result = build_calibration_history(_repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return CalibrationHistoryResponse(
        records=result["records"],
        drift_evidence=result["drift_evidence"],
        count=result["count"],
        boundary_confirmations=result["boundary_confirmations"],
    )
