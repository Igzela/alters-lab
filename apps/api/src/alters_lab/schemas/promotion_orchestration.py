"""Promotion orchestration plan schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class PromotionOrchestrationBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_only: bool = True
    active_yaml_modified: bool = False
    snapshot_yaml_modified: bool = False
    branches_yaml_modified: bool = False
    alters_modified: bool = False
    value_alignment_modified: bool = False
    dialogue_modified: bool = False
    reality_trace_modified: bool = False
    calibration_score_created: bool = False
    drift_computed: bool = False
    archive_created: bool = False
    provider_used: bool = False
    frontend_added: bool = False
    database_added: bool = False
    controlled_persist_api_called: bool = False
    draft_promoted_to_active: bool = False


class PromotionPlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    target_api: str
    method: str = "POST"
    payload_ref: str
    purpose: str
    requires_human_approval: bool = True
    execution_allowed_in_p3_m4: bool = False
    expected_artifact: str | None = None
    rollback_note: str

    @model_validator(mode="after")
    def validate_step(self) -> PromotionPlanStep:
        ALLOWED_APIS = {"/branches/persist", "/alters/persist-batch"}
        if self.target_api not in ALLOWED_APIS:
            raise ValueError(f"target_api '{self.target_api}' not in allowed: {ALLOWED_APIS}")
        if self.execution_allowed_in_p3_m4 is not False:
            raise ValueError("execution_allowed_in_p3_m4 must be false")
        if self.requires_human_approval is not True:
            raise ValueError("requires_human_approval must be true")
        return self


class PromotionEvidenceRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    required: bool = True
    description: str


class PromotionRollbackPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rollback_available: bool
    notes: list[str]
    required_backups: list[str]


class PromotionOrchestrationPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str
    schema_version: int = 1
    status: str = "promotion_plan"
    source_promotion_package_ref: str
    active_execution_allowed: bool = False
    requires_human_final_approval: bool = True
    steps: list[PromotionPlanStep]
    evidence_required: list[PromotionEvidenceRequirement]
    rollback_plan: PromotionRollbackPlan
    boundary_confirmations: PromotionOrchestrationBoundaryConfirmations
    created_at: str

    @model_validator(mode="after")
    def validate_plan(self) -> PromotionOrchestrationPlan:
        if self.status != "promotion_plan":
            raise ValueError(f"status must be 'promotion_plan', got '{self.status}'")
        if self.active_execution_allowed is not False:
            raise ValueError("active_execution_allowed must be false")
        if self.requires_human_final_approval is not True:
            raise ValueError("requires_human_final_approval must be true")
        if not self.steps:
            raise ValueError("steps must be non-empty")
        for step in self.steps:
            if step.execution_allowed_in_p3_m4 is True:
                raise ValueError(f"step {step.step_id}: execution_allowed_in_p3_m4 must be false")
        return self


class PromotionOrchestrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    save_plan: bool = False
    approval_token: str | None = None
    caller: str = "api"

    @model_validator(mode="after")
    def validate_request(self) -> PromotionOrchestrationRequest:
        if self.save_plan and (not self.approval_token or not self.approval_token.strip()):
            raise ValueError("approval_token required when save_plan=true")
        return self


class PromotionOrchestrationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    draft_id: str
    plan: PromotionOrchestrationPlan
    plan_path: str | None = None
    validation: dict
    boundary_confirmations: dict


class PromotionOrchestrationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    plans: list[dict]
    count: int
