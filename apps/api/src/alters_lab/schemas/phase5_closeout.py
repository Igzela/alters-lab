"""Pydantic schemas for P5-M7 Phase 5 Closeout."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CloseoutCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str  # "PASS" | "FAIL" | "NOTE"
    severity: str  # "critical" | "warning" | "info"
    message: str


class CloseoutSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_status: str
    total_checks: int
    passed: int
    failed: int
    notes: int
    sealed_baseline_candidate: bool = True


class Phase5CloseoutReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str  # "PASS" | "PASS_WITH_NOTES"
    summary: CloseoutSummary
    checks: list[CloseoutCheck]
    read_only: bool = True


class Phase5CloseoutEvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    evidence_path: str
    read_only: bool = True


class Phase5CloseoutHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "phase5-closeout"
    read_only: bool = True
