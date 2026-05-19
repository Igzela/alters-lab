from __future__ import annotations

from pydantic import BaseModel


class BoundaryConfirmations(BaseModel):
    read_only: bool = True
    active_yaml_modified: bool = False
    calibration_score_created: bool = False
    drift_computed: bool = False
    archive_created: bool = False
    provider_used: bool = False
    generation_runtime_used: bool = False


class CycleSummaryData(BaseModel):
    snapshot_phase: str | None = None
    branch_count: int | None = None
    alter_ids: list[str] | None = None
    primary_candidate: str | None = None
    selected_branch: str | None = None
    reality_trace_status: str | None = None
    day_14_gate: str | None = None
    day_30_gate: str | None = None
    calibration_ready: bool | None = None


class ValidationErrorDetail(BaseModel):
    ok: bool
    errors: list[str]
    warnings: list[str]


class CycleSummaryResponse(BaseModel):
    status: str = "ok"
    read_only: bool = True
    summary: CycleSummaryData
    validation: ValidationErrorDetail
    boundary_confirmations: BoundaryConfirmations


class CycleSummaryHealthResponse(BaseModel):
    status: str = "ok"
    component: str = "cycle-summary"
    mode: str = "read_only"


class ValidationResponse(BaseModel):
    status: str
    ok: bool
    errors: list[str]
    warnings: list[str]
    artifacts_checked: int


class ArtifactInfo(BaseModel):
    key: str
    path: str
    exists: bool


class ArtifactListResponse(BaseModel):
    status: str = "ok"
    read_only: bool = True
    artifacts: list[ArtifactInfo]
    count: int
