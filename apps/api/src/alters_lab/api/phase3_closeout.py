"""Phase 3 Closeout Gate API — read-only verification endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.phase3_closeout import (
    Phase3CloseoutBoundaryConfirmations,
    Phase3CloseoutResponse,
    Phase3CloseoutEvidenceResponse,
)
from alters_lab.services.phase3_closeout import (
    build_phase3_closeout_report,
    get_repo_root,
    phase3_closeout_boundary_confirmations,
    safe_read_json,
    write_phase3_closeout_artifacts,
)

router = APIRouter(prefix="/phase3-closeout", tags=["phase3-closeout"])


def _get_workspace() -> Path:
    return get_repo_root() / "docs" / "harness"


@router.get("/health")
def health():
    return {"status": "ok", "mode": "read_only_closeout"}


@router.get("/report")
def get_report():
    repo_root = get_repo_root()
    evidence_path = repo_root / "docs" / "harness" / "PHASE3_CLOSEOUT_EVIDENCE.json"

    if not evidence_path.exists():
        report = build_phase3_closeout_report(
            repo_root=repo_root,
            baseline_commit="unknown",
            test_count=None,
        )
        write_phase3_closeout_artifacts(report, repo_root)
    else:
        evidence = safe_read_json(evidence_path)
        report_data = evidence.get("report", evidence)
        report = build_phase3_closeout_report(
            repo_root=repo_root,
            baseline_commit=report_data.get("baseline_commit", "unknown"),
            test_count=report_data.get("test_count"),
        )

    return Phase3CloseoutResponse(
        status=report.status,
        report=report,
        boundary_confirmations=phase3_closeout_boundary_confirmations(),
    )


@router.get("/evidence")
def get_evidence():
    repo_root = get_repo_root()
    evidence_path = repo_root / "docs" / "harness" / "PHASE3_CLOSEOUT_EVIDENCE.json"

    if not evidence_path.exists():
        raise HTTPException(status_code=404, detail="Closeout evidence not found — run /report first")

    evidence = safe_read_json(evidence_path)
    return Phase3CloseoutEvidenceResponse(
        status="evidence_found",
        evidence=evidence,
        boundary_confirmations=phase3_closeout_boundary_confirmations(),
    )
