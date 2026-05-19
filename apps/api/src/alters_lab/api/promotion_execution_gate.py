"""Promotion execution gate API endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.promotion_execution_gate import (
    PromotionExecutionGateListResponse,
    PromotionExecutionGateRequest,
    PromotionExecutionGateResponse,
)
from alters_lab.services.promotion_execution_gate import (
    build_gate_report,
    list_execution_gate_reports,
    load_gate_inputs,
    promotion_execution_gate_boundary_confirmations,
    save_gate_report,
    validate_orchestration_plan_for_execution_gate,
    validate_promotion_package_for_execution_gate,
)

router = APIRouter(prefix="/promotion-execution-gate", tags=["promotion-execution-gate"])


def get_promotion_execution_gate_workspace() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "alters/drafts"


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "promotion-execution-gate",
        "mode": "gate_only",
        "dry_run_only": True,
        "live_execution_allowed": False,
        "provider_used": False,
    }


@router.post(
    "/{draft_id}/check",
    response_model=PromotionExecutionGateResponse,
)
def check_gate(draft_id: str, body: PromotionExecutionGateRequest):
    workspace = get_promotion_execution_gate_workspace()

    try:
        inputs = load_gate_inputs(workspace, draft_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    package = inputs["promotion_package"]
    plan = inputs["orchestration_plan"]

    pkg_validation = validate_promotion_package_for_execution_gate(package)
    plan_validation = validate_orchestration_plan_for_execution_gate(plan)

    if not pkg_validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"promotion package validation failed: {'; '.join(pkg_validation['errors'])}",
        )
    if not plan_validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"orchestration plan validation failed: {'; '.join(plan_validation['errors'])}",
        )

    report = build_gate_report(
        draft_id, package, plan, body.run_dry_run, body.final_approval_token
    )

    report_path = None
    packet_path = None
    if body.save_report:
        if not body.final_approval_token:
            raise HTTPException(status_code=400, detail="final_approval_token required when save_report=true")
        result = save_gate_report(workspace, draft_id, report, body.final_approval_token, body.caller)
        report_path = result["report_path"]
        packet_path = result["packet_path"]

    return PromotionExecutionGateResponse(
        status="report_saved" if body.save_report else report.status,
        draft_id=draft_id,
        report=report,
        report_path=report_path,
        packet_path=packet_path,
        boundary_confirmations=promotion_execution_gate_boundary_confirmations(),
    )


@router.get("/list", response_model=PromotionExecutionGateListResponse)
def list_reports():
    workspace = get_promotion_execution_gate_workspace()
    reports = list_execution_gate_reports(workspace)
    return PromotionExecutionGateListResponse(
        status="ok",
        reports=reports,
        count=len(reports),
    )
