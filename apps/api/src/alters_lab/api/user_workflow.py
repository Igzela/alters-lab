"""P5-M6 User Workflow Integration routes.

Integrated workflow state and optional workflow-run record.
No provider calls in state. No active YAML write.
"""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.user_workflow import (
    UserWorkflowHealthResponse,
    UserWorkflowStateResponse,
    WorkflowRunSummaryRequest,
    WorkflowRunSummaryResponse,
)
from alters_lab.services.user_workflow import (
    get_user_workflow_health,
    get_user_workflow_state,
    save_workflow_run_summary,
)

router = APIRouter(prefix="/user-workflow", tags=["user-workflow"])


@router.get("/health", response_model=UserWorkflowHealthResponse)
def health():
    return get_user_workflow_health()


@router.get("/state", response_model=UserWorkflowStateResponse)
def state():
    return get_user_workflow_state()


@router.post("/run-summary", response_model=WorkflowRunSummaryResponse)
def run_summary(request: WorkflowRunSummaryRequest):
    return save_workflow_run_summary(request)
