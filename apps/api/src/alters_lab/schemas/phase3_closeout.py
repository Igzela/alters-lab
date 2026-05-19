"""Pydantic schemas for Phase 3 Closeout Gate."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Phase3CloseoutBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")
    read_only: bool = True
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
    controlled_persist_called: bool = False
    live_execution_called: bool = False
    raw_audit_committed: bool = False
    runtime_drafts_committed: bool = False


class Phase3CloseoutCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    status: str  # PASS | WARN | FAIL
    severity: str  # blocking | warning | info
    message: str
    evidence_ref: str | None = None


class Phase3CloseoutSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phase: str = "Phase 3"
    status: str  # PASS | PASS_WITH_NOTES | BLOCKED
    total_checks: int
    passed_checks: int
    warning_checks: int
    failed_checks: int
    sealed_baseline_candidate: bool
    next_phase_status: str


class Phase3CloseoutReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: int = 1
    phase: str = "Phase 3"
    report_type: str = "controlled_mutation_closeout"
    status: str  # PASS | PASS_WITH_NOTES | BLOCKED
    baseline_commit: str
    test_count: int | None = None
    checks: list[Phase3CloseoutCheck]
    summary: Phase3CloseoutSummary
    boundary_confirmations: Phase3CloseoutBoundaryConfirmations
    created_at: str


class Phase3CloseoutResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    report: Phase3CloseoutReport
    boundary_confirmations: dict


class Phase3CloseoutEvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    evidence: dict
    boundary_confirmations: dict
