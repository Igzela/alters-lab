"""P6-M11 closeout routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.phase6_closeout import (
    Phase6CloseoutEvidenceResponse,
    Phase6CloseoutHealthResponse,
    Phase6CloseoutReportResponse,
)
from alters_lab.services.phase6_closeout import _get_repo_root, build_phase6_closeout_report

router = APIRouter(prefix="/phase6-closeout", tags=["phase6-closeout"])


@router.get("/health", response_model=Phase6CloseoutHealthResponse)
def health():
    return Phase6CloseoutHealthResponse()


@router.get("/report", response_model=Phase6CloseoutReportResponse)
def report():
    return build_phase6_closeout_report()


@router.get("/evidence", response_model=Phase6CloseoutEvidenceResponse)
def evidence():
    evidence_path = _get_repo_root() / "docs" / "harness" / "PHASE6_CLOSEOUT_EVIDENCE.json"
    if not evidence_path.exists():
        raise HTTPException(status_code=404, detail="Evidence file not found. P6 cannot be sealed before behavior validation.")
    return Phase6CloseoutEvidenceResponse(evidence_path=str(evidence_path))
