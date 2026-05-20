"""Checkpoint Regeneration Plan API for P4-M7."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.checkpoint_regeneration import (
    CheckpointHealthResponse,
    CheckpointPlanListResponse,
    CheckpointPlanRequest,
    CheckpointPlanResponse,
)
from alters_lab.services.calibration_loop import get_repo_root
from alters_lab.services.checkpoint_regeneration import (
    checkpoint_boundary_confirmations,
    list_checkpoint_regeneration_plans,
    plan_checkpoint_regeneration,
)

router = APIRouter(prefix="/checkpoint-regeneration", tags=["checkpoint-regeneration"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=CheckpointHealthResponse)
def health():
    return CheckpointHealthResponse()


@router.post("/plan", response_model=CheckpointPlanResponse)
def plan(request: CheckpointPlanRequest):
    try:
        status, plan_result, path = plan_checkpoint_regeneration(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return CheckpointPlanResponse(
        status=status,  # type: ignore[arg-type]
        plan=plan_result,
        plan_path=str(path) if path else None,
        boundary_confirmations=checkpoint_boundary_confirmations(),
    )


@router.get("/list", response_model=CheckpointPlanListResponse)
def list_plans():
    plans = list_checkpoint_regeneration_plans(_repo_root())
    return CheckpointPlanListResponse(
        status="ok",
        plans=plans,
        count=len(plans),
        boundary_confirmations=checkpoint_boundary_confirmations(),
    )
