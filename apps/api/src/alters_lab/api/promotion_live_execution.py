"""Promotion live execution API endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.promotion_live_execution import (
    PromotionLiveExecutionListResponse,
    PromotionLiveExecutionRequest,
    PromotionLiveExecutionResponse,
)
from alters_lab.services.promotion_live_execution import (
    list_live_execution_reports,
    promotion_live_execution_boundary_confirmations,
    run_live_execution_gate,
    save_live_execution_report,
)

router = APIRouter(prefix="/promotion-live-execution", tags=["promotion-live-execution"])


def get_promotion_live_execution_workspace() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "alters/drafts"


LIVE_EXECUTION_ENABLED = False


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "promotion-live-execution",
        "mode": "controlled_live_runtime",
        "default_live_execution_enabled": LIVE_EXECUTION_ENABLED,
        "provider_used": False,
        "database_added": False,
        "frontend_added": False,
    }


@router.post(
    "/{draft_id}/run",
    response_model=PromotionLiveExecutionResponse,
)
def run_live_execution(draft_id: str, body: PromotionLiveExecutionRequest):
    workspace = get_promotion_live_execution_workspace()

    if body.mode == "live" and not LIVE_EXECUTION_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="live execution not enabled on this server; set LIVE_EXECUTION_ENABLED=true to allow",
        )

    try:
        report = run_live_execution_gate(
            draft_workspace=workspace,
            draft_id=draft_id,
            request_mode=body.mode,
            final_execution_token=body.final_execution_token,
            require_matching_gate_token=body.require_matching_gate_token,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    report_path = None
    if body.save_report:
        save_result = save_live_execution_report(
            draft_workspace=workspace,
            draft_id=draft_id,
            report=report,
            final_execution_token=body.final_execution_token,
            caller=body.caller,
        )
        report_path = save_result["report_path"]

    boundary = promotion_live_execution_boundary_confirmations(
        active_yaml_modified=False,
        branches_yaml_modified=any(
            r.target_api == "/branches/persist" and r.status == "executed"
            for r in report.step_results
        ),
        alters_modified=any(
            r.target_api == "/alters/persist-batch" and r.status == "executed"
            for r in report.step_results
        ),
        draft_promoted_to_active=report.status == "live_executed",
    )

    return PromotionLiveExecutionResponse(
        status=report.status,
        draft_id=draft_id,
        report=report,
        report_path=report_path,
        boundary_confirmations=boundary,
    )


@router.get("/list", response_model=PromotionLiveExecutionListResponse)
def list_reports():
    workspace = get_promotion_live_execution_workspace()
    reports = list_live_execution_reports(workspace)
    return PromotionLiveExecutionListResponse(
        status="ok",
        executions=reports,
        count=len(reports),
    )
