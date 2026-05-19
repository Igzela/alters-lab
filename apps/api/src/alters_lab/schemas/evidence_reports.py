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


class EvidenceStatusResponse(BaseModel):
    status: str = "ok"
    read_only: bool = True
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
