"""P5-M7 Phase 5 Closeout routes.

Read-only report and evidence endpoints. Artifact generation via service/manual command only.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.phase5_closeout import (
    Phase5CloseoutEvidenceResponse,
    Phase5CloseoutHealthResponse,
    Phase5CloseoutReportResponse,
)
from alters_lab.services.phase5_closeout import (
    build_phase5_closeout_report,
    _get_repo_root,
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
    root = _get_repo_root()
    evidence_path = root / "docs" / "harness" / "PHASE5_CLOSEOUT_EVIDENCE.json"
    if not evidence_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Evidence file not found. Run closeout artifact generation manually.",
        )
    return Phase5CloseoutEvidenceResponse(evidence_path=str(evidence_path))
