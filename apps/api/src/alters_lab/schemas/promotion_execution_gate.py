"""Promotion execution gate schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class PromotionExecutionGateBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_only: bool = True
    dry_run_only: bool = True
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
    live_persist_called: bool = False
    controlled_persist_api_called: bool = False
    draft_promoted_to_active: bool = False


class ExecutionPrerequisiteCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    passed: bool
    severity: str = "blocking"
    message: str

    @model_validator(mode="after")
    def validate_severity(self) -> ExecutionPrerequisiteCheck:
        allowed = {"blocking", "warning", "info"}
        if self.severity not in allowed:
            raise ValueError(f"severity must be one of {allowed}, got '{self.severity}'")
        return self


class DryRunCheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_api: str
    attempted: bool
    passed: bool
    dry_run_only: bool = True
    payload_ref: str
    message: str
    expected_artifact: str | None = None

    @model_validator(mode="after")
    def validate_dry_run(self) -> DryRunCheckResult:
        ALLOWED_APIS = {"/branches/persist", "/alters/persist-batch"}
        if self.target_api not in ALLOWED_APIS:
            raise ValueError(f"target_api '{self.target_api}' not in allowed: {ALLOWED_APIS}")
        if self.dry_run_only is not True:
            raise ValueError("dry_run_only must be true")
        return self


class ExecutionPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str
    schema_version: int = 1
    status: str = "execution_packet"
    execution_allowed_now: bool = False
    live_execution_allowed_in_p3_m5: bool = False
    requires_p3_m6_live_execution: bool = True
    final_approval_token_hash: str | None = None
    source_promotion_package_ref: str
    source_orchestration_plan_ref: str
    ordered_steps: list[dict]
    dry_run_results: list[DryRunCheckResult]
    prerequisites: list[ExecutionPrerequisiteCheck]
    evidence_required: list[dict]
    boundary_confirmations: PromotionExecutionGateBoundaryConfirmations
    created_at: str

    @model_validator(mode="after")
    def validate_packet(self) -> ExecutionPacket:
        if self.status != "execution_packet":
            raise ValueError(f"status must be 'execution_packet', got '{self.status}'")
        if self.execution_allowed_now is not False:
            raise ValueError("execution_allowed_now must be false")
        if self.live_execution_allowed_in_p3_m5 is not False:
            raise ValueError("live_execution_allowed_in_p3_m5 must be false")
        if self.requires_p3_m6_live_execution is not True:
            raise ValueError("requires_p3_m6_live_execution must be true")
        for dr in self.dry_run_results:
            if dr.dry_run_only is not True:
                raise ValueError(f"dry_run {dr.target_api}: dry_run_only must be true")
        return self


class PromotionExecutionGateReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str
    schema_version: int = 1
    status: str
    gate_passed: bool
    blocking_failures: list[str]
    warnings: list[str]
    execution_packet: ExecutionPacket | None = None
    boundary_confirmations: PromotionExecutionGateBoundaryConfirmations
    created_at: str

    @model_validator(mode="after")
    def validate_report(self) -> PromotionExecutionGateReport:
        allowed_status = {"gate_passed", "gate_failed"}
        if self.status not in allowed_status:
            raise ValueError(f"status must be one of {allowed_status}, got '{self.status}'")
        return self


class PromotionExecutionGateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_dry_run: bool = True
    save_report: bool = False
    final_approval_token: str | None = None
    caller: str = "api"

    @model_validator(mode="after")
    def validate_request(self) -> PromotionExecutionGateRequest:
        if self.save_report and (not self.final_approval_token or not self.final_approval_token.strip()):
            raise ValueError("final_approval_token required when save_report=true")
        return self


class PromotionExecutionGateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    draft_id: str
    report: PromotionExecutionGateReport
    report_path: str | None = None
    packet_path: str | None = None
    boundary_confirmations: dict


class PromotionExecutionGateListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    reports: list[dict]
    count: int
