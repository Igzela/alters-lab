"""P6-M11 closeout schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Phase6CloseoutCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    severity: str
    message: str


class Phase6CloseoutSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_status: str
    total_checks: int
    passed: int
    failed: int
    notes: int
    sealed_baseline_candidate: bool = False


class Phase6CloseoutReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    summary: Phase6CloseoutSummary
    checks: list[Phase6CloseoutCheck]
    read_only: bool = True


class Phase6CloseoutEvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    evidence_path: str
    read_only: bool = True


class Phase6CloseoutHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "phase6-closeout"
    read_only: bool = True
    requires_behavior_validation: bool = True
