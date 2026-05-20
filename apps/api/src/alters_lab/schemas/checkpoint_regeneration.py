"""Pydantic schemas for P4-M7 Checkpoint Regeneration Plan."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CheckpointBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_only: bool = True
    active_yaml_modified: bool = False
    branch_alter_semantics_modified: bool = False
    provider_used: bool = False
    frontend_added: bool = False
    database_added: bool = False
    archive_created: bool = False
    regeneration_executed: bool = False
    human_confirmation_required: bool = True


class CheckpointRegenerationPlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    title: str
    description: str
    required_evidence: list[str]
    execution_allowed_now: bool = False

    @field_validator("execution_allowed_now")
    @classmethod
    def validate_execution_allowed_now(cls, value: bool) -> bool:
        if value is not False:
            raise ValueError("execution_allowed_now must be false")
        return value


class CheckpointRegenerationPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    status: str = "pending_review"
    trigger_reason: str
    source_drift_refs: list[str]
    source_score_refs: list[str]
    recommended_scope: Literal[
        "no_action",
        "review_rubric",
        "review_alter",
        "review_branch",
        "full_checkpoint_review",
    ]
    steps: list[CheckpointRegenerationPlanStep]
    regeneration_allowed_now: bool = False
    active_write_allowed: bool = False
    human_confirmation_required: bool = True
    created_at: str
    boundary_confirmations: CheckpointBoundaryConfirmations

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value != "pending_review":
            raise ValueError("status must be pending_review")
        return value

    @field_validator("regeneration_allowed_now")
    @classmethod
    def validate_regeneration_allowed_now(cls, value: bool) -> bool:
        if value is not False:
            raise ValueError("regeneration_allowed_now must be false")
        return value

    @field_validator("active_write_allowed")
    @classmethod
    def validate_active_write_allowed(cls, value: bool) -> bool:
        if value is not False:
            raise ValueError("active_write_allowed must be false")
        return value

    @field_validator("human_confirmation_required")
    @classmethod
    def validate_human_confirmation_required(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("human_confirmation_required must be true")
        return value


class CheckpointPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drift_threshold: float = Field(default=0.6, ge=0, le=1)
    save_plan: bool = False
    caller: str = "api"


class CheckpointPlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["plan_created", "no_action", "saved", "rejected"]
    plan: CheckpointRegenerationPlan | None
    plan_path: str | None
    boundary_confirmations: dict


class CheckpointPlanListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    plans: list[dict]
    count: int
    boundary_confirmations: dict


class CheckpointHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "checkpoint-regeneration"
    mode: str = "plan_only_no_active_regeneration"
    provider_used: bool = False
    active_write_allowed: bool = False
    regeneration_allowed_now: bool = False
