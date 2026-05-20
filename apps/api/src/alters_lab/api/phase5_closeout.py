"""P5-M7 Phase 5 Closeout routes.

Read-only report and evidence endpoints. Artifact generation via service.
"""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.phase5_closeout import (
    Phase5CloseoutEvidenceResponse,
    Phase5CloseoutHealthResponse,
    Phase5CloseoutReportResponse,
)
from alters_lab.services.phase5_closeout import (
    build_phase5_closeout_report,
    write_phase5_closeout_artifacts,
)

router = APIRouter(prefix="/phase5-closeout", tags=["phase5-closeout"])


@router.get("/health", response_model=Phase5CloseoutHealthResponse)
def health():
    return Phase5CloseoutHealthResponse()


@router.get("/report", response_model=Phase5CloseoutReportResponse)
def report():
    return build_phase5_closeout_report()


@router.get("/evidence", response_model=Phase5CloseoutEvidenceResponse)
def evidence():
    report = build_phase5_closeout_report()
    path = write_phase5_closeout_artifacts(report)
    return Phase5CloseoutEvidenceResponse(evidence_path=path)
