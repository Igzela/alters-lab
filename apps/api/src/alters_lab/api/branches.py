"""Controlled Branches Write API endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.branches import (
    BranchesPersistRequest,
    BranchesPersistResponse,
)
from alters_lab.services.branches_persist import (
    preview_branches_persist,
    validate_branches_governance,
    write_branches_with_audit,
)

router = APIRouter(prefix="/branches", tags=["branches"])


def get_branches_persist_target_path() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "alters/current/branches.yaml"


def get_branches_persist_audit_log_path() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "docs/harness/phase3_write_audit.jsonl"


def get_branches_persist_backup_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "docs/harness/backups/phase3"


@router.get("/health")
def health():
    return {"status": "ok", "component": "branches", "mode": "controlled_write"}


@router.post(
    "/persist",
    response_model=BranchesPersistResponse,
)
def persist_branches(body: BranchesPersistRequest):
    payload = body.to_payload()
    governance = validate_branches_governance(payload)
    if not governance["valid"]:
        raise HTTPException(
            status_code=403,
            detail=f"governance validation failed: {'; '.join(governance['errors'])}",
        )

    target = get_branches_persist_target_path()
    audit_log = get_branches_persist_audit_log_path()
    backup = get_branches_persist_backup_dir()

    if body.dry_run:
        result = preview_branches_persist(payload, target)
        boundary = {
            "branches_yaml_modified": False,
            "snapshot_yaml_modified": False,
            "alters_modified": False,
            "value_alignment_modified": False,
            "dialogue_modified": False,
            "reality_trace_modified": False,
            "calibration_score_created": False,
            "drift_computed": False,
            "archive_created": False,
            "provider_used": False,
            "frontend_added": False,
            "database_added": False,
            "generation_runtime_used": False,
        }
        return BranchesPersistResponse(
            status=result["status"],
            target_path=result["target_path"],
            pre_write_hash=result["pre_write_hash"],
            post_write_hash=None,
            audit_log_path=None,
            backup_path=None,
            governance_check=governance,
            boundary_confirmations=boundary,
        )

    result = write_branches_with_audit(
        payload,
        target,
        audit_log,
        body.approval_token,
        caller=body.caller,
        create_backup=True,
        backup_dir=backup,
    )

    if result["status"] == "rejected":
        raise HTTPException(status_code=403, detail=result["reason"])

    boundary = {
        "branches_yaml_modified": True,
        "snapshot_yaml_modified": False,
        "alters_modified": False,
        "value_alignment_modified": False,
        "dialogue_modified": False,
        "reality_trace_modified": False,
        "calibration_score_created": False,
        "drift_computed": False,
        "archive_created": False,
        "provider_used": False,
        "frontend_added": False,
        "database_added": False,
        "generation_runtime_used": False,
    }

    return BranchesPersistResponse(
        status=result["status"],
        target_path=result["target_path"],
        pre_write_hash=result["pre_write_hash"],
        post_write_hash=result["post_write_hash"],
        audit_log_path=result["audit_log_path"],
        backup_path=result.get("backup_path"),
        governance_check=governance,
        boundary_confirmations=boundary,
    )
