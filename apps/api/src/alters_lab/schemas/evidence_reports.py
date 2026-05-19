from __future__ import annotations

from pydantic import BaseModel


class EvidenceHealthResponse(BaseModel):
    status: str = "ok"
    component: str = "evidence-reports"
    mode: str = "read_only"


class Day30DemoSummary(BaseModel):
    status: str
    exists: bool
    overall: str | None = None
    total_steps: int | None = None
    passed_steps: int | None = None
    all_pass: bool | None = None
    error: str | None = None


class ActiveYamlValidationSummary(BaseModel):
    status: str
    exists: bool
    ok: bool | None = None
    snapshot_phase: str | None = None
    branch_count: int | None = None
    alter_ids: list[str] | None = None
    primary_candidate: str | None = None
    selected_branch: str | None = None
    reality_trace_status: str | None = None
    day_14_gate: str | None = None
    day_30_gate: str | None = None
    calibration_ready: bool | None = None
    error: str | None = None


class Phase1CloseoutSummary(BaseModel):
    status: str
    exists: bool
    title: str | None = None
    line_count: int | None = None
    contains_sealed_baseline: bool | None = None
    contains_final_gate_pass: bool | None = None


class EvidenceBoundaryConfirmations(BaseModel):
    no_provider_imports: bool = True
    no_database_imports: bool = True
    no_frontend_code: bool = True
    no_env_file: bool = True
    no_dialogue_runtime: bool = True
    no_calibration_runtime: bool = True
    no_archive_runtime: bool = True
    no_score_yaml: bool = True
    no_archive_folders: bool = True
    no_active_yaml_mutation: bool = True
    read_only_validation_enforced: bool = True


class EvidenceStatusResponse(BaseModel):
    status: str = "ok"
    read_only: bool = True
    boundary_confirmations: EvidenceBoundaryConfirmations
    day30_demo: Day30DemoSummary
    active_yaml_validation: ActiveYamlValidationSummary
    phase1_closeout: Phase1CloseoutSummary


class EvidenceReportInfo(BaseModel):
    key: str
    path: str
    exists: bool
    format: str


class EvidenceReportsResponse(BaseModel):
    status: str = "ok"
    read_only: bool = True
    reports: list[EvidenceReportInfo]
    count: int
