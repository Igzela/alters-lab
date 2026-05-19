"""Promotion live execution schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class PromotionLiveExecutionBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    live_execution_runtime_added: bool = True
    direct_yaml_write_used: bool = False
    controlled_persist_services_used: bool = True
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
    http_persist_route_called: bool = False
    draft_promoted_to_active: bool = False


class LiveExecutionStepResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    target_api: str
    executed: bool
    dry_run: bool
    status: str
    target_path: str | None = None
    pre_write_hash: str | None = None
    post_write_hash: str | None = None
    backup_path: str | None = None
    audit_log_path: str | None = None
    message: str

    @model_validator(mode="after")
    def validate_step(self) -> LiveExecutionStepResult:
        ALLOWED_APIS = {"/branches/persist", "/alters/persist-batch"}
        if self.target_api not in ALLOWED_APIS:
            raise ValueError(f"target_api '{self.target_api}' not in allowed: {ALLOWED_APIS}")
        allowed_status = {"skipped", "dry_run_passed", "dry_run_failed", "executed", "failed"}
        if self.status not in allowed_status:
            raise ValueError(f"status must be one of {allowed_status}, got '{self.status}'")
        if self.dry_run and self.executed:
            raise ValueError("executed must be false when dry_run=true")
        return self


class PromotionLiveExecutionReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str
    schema_version: int = 1
    status: str
    live_execution_performed: bool
    dry_run_only: bool
    final_execution_token_hash: str | None = None
    source_promotion_package_ref: str
    source_orchestration_plan_ref: str
    source_gate_report_ref: str
    source_execution_packet_ref: str
    step_results: list[LiveExecutionStepResult]
    blocking_failures: list[str]
    boundary_confirmations: PromotionLiveExecutionBoundaryConfirmations
    created_at: str

    @model_validator(mode="after")
    def validate_report(self) -> PromotionLiveExecutionReport:
        allowed_status = {"dry_run_passed", "dry_run_failed", "live_executed", "live_failed", "rejected"}
        if self.status not in allowed_status:
            raise ValueError(f"status must be one of {allowed_status}, got '{self.status}'")
        if self.dry_run_only and self.live_execution_performed:
            raise ValueError("live_execution_performed must be false when dry_run_only=true")
        if self.status == "live_executed" and not self.live_execution_performed:
            raise ValueError("live_execution_performed must be true when status is live_executed")
        if self.status.startswith("dry_run") and self.live_execution_performed:
            raise ValueError("live_execution_performed must be false when status starts with dry_run")
        return self


class PromotionLiveExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str = "dry_run"
    final_execution_token: str | None = None
    save_report: bool = False
    caller: str = "api"
    require_matching_gate_token: bool = True

    @model_validator(mode="after")
    def validate_request(self) -> PromotionLiveExecutionRequest:
        allowed_mode = {"dry_run", "live"}
        if self.mode not in allowed_mode:
            raise ValueError(f"mode must be one of {allowed_mode}, got '{self.mode}'")
        if self.mode == "live" and (not self.final_execution_token or not self.final_execution_token.strip()):
            raise ValueError("final_execution_token required when mode=live")
        if self.save_report and (not self.final_execution_token or not self.final_execution_token.strip()):
            raise ValueError("final_execution_token required when save_report=true")
        return self


class PromotionLiveExecutionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    draft_id: str
    report: PromotionLiveExecutionReport
    report_path: str | None = None
    boundary_confirmations: dict


class PromotionLiveExecutionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    executions: list[dict]
    count: int
