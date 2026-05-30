"""Phase 4 Closeout API — read-only verification endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.phase4_closeout import (
    Phase4CloseoutEvidenceResponse,
    Phase4CloseoutResponse,
)
from alters_lab.services import io
from alters_lab.services.phase4_closeout import (
    build_phase4_closeout_report,
    get_repo_root,
    phase4_closeout_boundary_confirmations,
)

router = APIRouter(prefix="/phase4-closeout", tags=["phase4-closeout"])


@router.get("/health")
def health():
    return {"status": "ok", "mode": "read_only_phase4_closeout"}


@router.get("/report", response_model=Phase4CloseoutResponse)
def get_report():
    report = build_phase4_closeout_report(repo_root=get_repo_root())
    return Phase4CloseoutResponse(
        status=report.status,
        report=report,
        boundary_confirmations=phase4_closeout_boundary_confirmations(),
    )


@router.get("/evidence", response_model=Phase4CloseoutEvidenceResponse)
def get_evidence():
    evidence_path = get_repo_root() / "docs" / "harness" / "PHASE4_CLOSEOUT_EVIDENCE.json"
    if not evidence_path.exists():
        raise HTTPException(status_code=404, detail="Phase 4 closeout evidence not found")
    return Phase4CloseoutEvidenceResponse(
        status="evidence_found",
        evidence=io.read_json(evidence_path),
        boundary_confirmations=phase4_closeout_boundary_confirmations(),
    )
