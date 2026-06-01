"""External evidence API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.services.external_evidence import (
    list_evidence,
    load_evidence,
    save_evidence,
)

router = APIRouter(prefix="/external-evidence", tags=["external-evidence"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "external-evidence",
        "storage_area": "alters/product/external_evidence",
        "provider_required": False,
    }


@router.post("")
def create_evidence(body: ExternalEvidenceRecord):
    try:
        path = save_evidence(body)
        return {
            "status": "saved",
            "evidence": body.model_dump(),
            "evidence_path": str(path),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/list")
def list_all():
    evidence = list_evidence()
    return {
        "status": "ok",
        "evidence": [e.model_dump() for e in evidence],
        "count": len(evidence),
    }


@router.get("/{evidence_id}")
def get_evidence(evidence_id: str):
    try:
        evidence = load_evidence(evidence_id)
        return {"status": "ok", "evidence": evidence.model_dump()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Evidence not found: {evidence_id}"
        )
