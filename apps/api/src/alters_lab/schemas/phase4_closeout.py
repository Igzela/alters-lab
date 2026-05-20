"""Pydantic schemas for Phase 4 Closeout."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Phase4CloseoutBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    read_only: bool = True
    active_yaml_modified: bool = False
    snapshot_yaml_modified: bool = False
    rubric_modified: bool = False
    provider_used: bool = False
    provider_config_added: bool = False
    frontend_added: bool = False
    database_added: bool = False
    live_execution_called: bool = False
    controlled_persist_called_for_active_yaml: bool = False
    automatic_regeneration_triggered: bool = False
    automatic_archive_triggered: bool = False
    raw_runtime_artifacts_committed: bool = False
    phase5_started: bool = False


class Phase4CloseoutCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    severity: str
    message: str
    evidence_ref: str | None = None


class Phase4CloseoutSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phase: str = "Phase 4"
    status: str
    total_checks: int
    passed_checks: int
    warning_checks: int
    failed_checks: int
    sealed_baseline_candidate: bool
    next_phase_status: str


class Phase4CloseoutReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    phase: str = "Phase 4"
    report_type: str = "backend_calibration_loop_closeout"
    status: str
    baseline_commit: str
    test_count: int | None = None
    checks: list[Phase4CloseoutCheck]
    summary: Phase4CloseoutSummary
    boundary_confirmations: Phase4CloseoutBoundaryConfirmations
    created_at: str


class Phase4CloseoutResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    report: Phase4CloseoutReport
    boundary_confirmations: dict


class Phase4CloseoutEvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    evidence: dict
    boundary_confirmations: dict
