"""Dynamic weight API router."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.dynamic_weight import (
    DynamicWeightHealthResponse,
    DynamicWeightRequest,
    DynamicWeightResult,
)
from alters_lab.services.dynamic_weight import compute_dynamic_weights
from alters_lab.services.calibration_loop import get_repo_root

router = APIRouter(prefix="/dynamic-weight", tags=["dynamic-weight"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=DynamicWeightHealthResponse)
def health():
    return DynamicWeightHealthResponse()


@router.post("/compute", response_model=DynamicWeightResult)
def compute(request: DynamicWeightRequest):
    try:
        return compute_dynamic_weights(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
