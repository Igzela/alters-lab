"""Pydantic schemas for P5-M6 User Workflow Integration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UserWorkflowStateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    available_alters: list[str]
    provider_status: str
    last_reality_scores: list[dict] = Field(default_factory=list)
    drift_summary: dict | None = None
    rubric_delta_available: bool = False
    checkpoint_plan_available: bool = False
    next_recommended_action: str = "select_an_alter"
    read_only: bool = True


class WorkflowRunSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    alter_id: str | None = None
    notes: str = ""
    caller: str = "api"


class WorkflowRunSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    run_id: str
    run_path: str | None = None
    active_yaml_modified: bool = False
    persisted: bool = False


class UserWorkflowHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "user-workflow"
    read_only: bool = True
