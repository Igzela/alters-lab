"""Promotion orchestration plan API endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.promotion_orchestration import (
    PromotionOrchestrationListResponse,
    PromotionOrchestrationRequest,
    PromotionOrchestrationResponse,
)
from alters_lab.services.promotion_orchestration import (
    build_orchestration_plan,
    list_orchestration_plans,
    load_promotion_package,
    promotion_orchestration_boundary_confirmations,
    save_orchestration_plan,
    validate_promotion_package_for_orchestration,
)

router = APIRouter(prefix="/promotion-orchestration", tags=["promotion-orchestration"])


def get_promotion_orchestration_workspace() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "alters/drafts"


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "promotion-orchestration",
        "mode": "plan_only",
        "active_execution_allowed": False,
        "provider_used": False,
    }


@router.post(
    "/{draft_id}/plan",
    response_model=PromotionOrchestrationResponse,
)
def create_plan(draft_id: str, body: PromotionOrchestrationRequest):
    workspace = get_promotion_orchestration_workspace()

    try:
        package = load_promotion_package(workspace, draft_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Promotion package not found: {draft_id}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    validation = validate_promotion_package_for_orchestration(package)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"promotion package validation failed: {'; '.join(validation['errors'])}",
        )

    plan = build_orchestration_plan(workspace, draft_id)

    plan_path = None
    if body.save_plan:
        result = save_orchestration_plan(workspace, draft_id, plan, body.approval_token, body.caller)
        plan_path = result["plan_path"]

    return PromotionOrchestrationResponse(
        status="plan_saved" if body.save_plan else "plan_generated",
        draft_id=draft_id,
        plan=plan,
        plan_path=plan_path,
        validation=validation,
        boundary_confirmations=promotion_orchestration_boundary_confirmations(),
    )


@router.get("/list", response_model=PromotionOrchestrationListResponse)
def list_plans():
    workspace = get_promotion_orchestration_workspace()
    plans = list_orchestration_plans(workspace)
    return PromotionOrchestrationListResponse(
        status="ok",
        plans=plans,
        count=len(plans),
    )
