"""Controlled Alter Write API endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.alters import (
    AlterBatchPersistRequest,
    AlterBatchPersistResponse,
    AlterPersistRequest,
    AlterPersistResponse,
)
from alters_lab.services.alters_persist import (
    get_alter_target_path,
    preview_alter_persist,
    validate_alter_governance,
    validate_batch_governance,
    write_alter_batch_with_audit,
    write_alter_with_audit,
)

router = APIRouter(prefix="/alters", tags=["alters"])


def get_alters_persist_base_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "alters/current/alters"


def get_alters_persist_audit_log_path() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "docs/harness/phase3_write_audit.jsonl"


def get_alters_persist_backup_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "docs/harness/backups/phase3"


@router.get("/health")
def health():
    return {"status": "ok", "component": "alters"}


@router.post(
    "/persist/{alter_id}",
    response_model=AlterPersistResponse,
)
def persist_alter(alter_id: str, body: AlterPersistRequest):
    payload = body.to_payload()
    if payload.id != alter_id:
        raise HTTPException(status_code=400, detail=f"alter_id mismatch: path has {alter_id}, payload has {payload.id}")

    governance = validate_alter_governance(payload)
    if not governance["valid"]:
        raise HTTPException(
            status_code=403,
            detail=f"governance validation failed: {'; '.join(governance['errors'])}",
        )

    base_dir = get_alters_persist_base_dir()
    target = get_alter_target_path(alter_id, base_dir)
    audit_log = get_alters_persist_audit_log_path()
    backup = get_alters_persist_backup_dir()

    if body.dry_run:
        result = preview_alter_persist(payload, target)
        boundary = {
            "alters_modified": False,
            "snapshot_yaml_modified": False,
            "branches_yaml_modified": False,
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
        return AlterPersistResponse(
            status=result["status"],
            target_path=result["target_path"],
            pre_write_hash=result["pre_write_hash"],
            post_write_hash=None,
            audit_log_path=None,
            backup_path=None,
            governance_check=governance,
            boundary_confirmations=boundary,
        )

    result = write_alter_with_audit(
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
        "alters_modified": True,
        "snapshot_yaml_modified": False,
        "branches_yaml_modified": False,
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

    return AlterPersistResponse(
        status=result["status"],
        target_path=result["target_path"],
        pre_write_hash=result["pre_write_hash"],
        post_write_hash=result["post_write_hash"],
        audit_log_path=result["audit_log_path"],
        backup_path=result.get("backup_path"),
        governance_check=governance,
        boundary_confirmations=boundary,
    )


@router.post(
    "/persist-batch",
    response_model=AlterBatchPersistResponse,
)
def persist_alter_batch(body: AlterBatchPersistRequest):
    governance = validate_batch_governance(body.alters)
    if not governance["valid"]:
        raise HTTPException(
            status_code=403,
            detail=f"governance validation failed: {'; '.join(governance['errors'])}",
        )

    base_dir = get_alters_persist_base_dir()
    audit_log = get_alters_persist_audit_log_path()
    backup = get_alters_persist_backup_dir()

    if body.dry_run:
        boundary = {
            "alters_modified": False,
            "snapshot_yaml_modified": False,
            "branches_yaml_modified": False,
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
        return AlterBatchPersistResponse(
            status="dry_run",
            written_paths=[],
            pre_write_hashes={},
            post_write_hashes={},
            audit_log_path=None,
            governance_check=governance,
            boundary_confirmations=boundary,
        )

    result = write_alter_batch_with_audit(
        body.alters,
        base_dir,
        audit_log,
        body.approval_token,
        caller=body.caller,
        create_backup=True,
        backup_dir=backup,
    )

    if result["status"] == "rejected":
        raise HTTPException(status_code=403, detail=result["reason"])

    boundary = {
        "alters_modified": True,
        "snapshot_yaml_modified": False,
        "branches_yaml_modified": False,
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

    return AlterBatchPersistResponse(
        status=result["status"],
        written_paths=result["written_paths"],
        pre_write_hashes=result["pre_write_hashes"],
        post_write_hashes=result["post_write_hashes"],
        audit_log_path=result["audit_log_path"],
        governance_check=governance,
        boundary_confirmations=boundary,
    )
