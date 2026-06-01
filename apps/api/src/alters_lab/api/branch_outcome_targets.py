"""Branch outcome targets API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.branch_outcome_targets import BranchOutcomeTargetRecord
from alters_lab.services.branch_outcome_targets import (
    evaluate_existing_target,
    list_targets,
    load_target,
    save_target,
)

router = APIRouter(prefix="/branch-outcome-targets", tags=["branch-outcome-targets"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "branch-outcome-targets",
        "storage_area": "alters/product/branch_outcome_targets",
        "provider_required": False,
    }


@router.post("")
def create_target(body: BranchOutcomeTargetRecord):
    try:
        path = save_target(body)
        return {
            "status": "saved",
            "target": body.model_dump(),
            "target_path": str(path),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/list")
def list_all():
    targets = list_targets()
    return {
        "status": "ok",
        "targets": [t.model_dump() for t in targets],
        "count": len(targets),
    }


@router.get("/{target_id}")
def get_target(target_id: str):
    try:
        target = load_target(target_id)
        return {"status": "ok", "target": target.model_dump()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Target not found: {target_id}"
        )


@router.post("/{target_id}/evaluate")
def evaluate(target_id: str, body: dict):
    try:
        final_value = body.get("final_observed_value")
        achieved = body.get("achieved", False)
        if not final_value:
            raise HTTPException(status_code=400, detail="final_observed_value is required")
        result = evaluate_existing_target(target_id, final_value, achieved)
        return {"status": "evaluated", "target": result.model_dump()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Target not found: {target_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
