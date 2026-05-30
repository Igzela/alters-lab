"""Controlled Branches Write API — persist confirmed branch discovery to disk."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from alters_lab.schemas.branches import BranchDiscoveryPayload
from alters_lab.services import io
from alters_lab.services.controlled_write import (
    append_jsonl_audit,
    create_backup_if_exists,
    hash_approval_token,
    reject_blank_token,
    sha256_file,
    sha256_text,
)


def branches_to_yaml(payload: BranchDiscoveryPayload) -> str:
    d = {
        "branch_discovery": payload.branch_discovery.model_dump(mode="json"),
        "branches": [b.model_dump(mode="json") for b in payload.branches],
    }
    return io.dump_yaml_str(d)


def validate_branches_governance(payload: BranchDiscoveryPayload) -> dict:
    errors: list[str] = []

    if payload.branch_discovery.status != "completed":
        errors.append("branch_discovery.status must be 'completed'")

    if payload.branch_discovery.source_snapshot_ref != "alters/current/snapshot.yaml":
        errors.append("branch_discovery.source_snapshot_ref must be 'alters/current/snapshot.yaml'")

    if len(payload.branches) != 4:
        errors.append("exactly 4 branches required")

    expected_ids = {"branch_A", "branch_B", "branch_C", "branch_D"}
    actual_ids = {b.id for b in payload.branches}
    if actual_ids != expected_ids:
        errors.append(f"branch ids must be {expected_ids}")

    for b in payload.branches:
        if not b.incompatible_with:
            errors.append(f"branch {b.id} must have non-empty incompatible_with")

    forbidden_fields = ["alter_generation", "dialogue", "calibration", "archive", "provider", "runtime"]
    for field in forbidden_fields:
        if hasattr(payload, field) or field in payload.model_fields_set:
            errors.append(f"payload must not contain forbidden field: {field}")

    return {"valid": len(errors) == 0, "errors": errors}


def preview_branches_persist(payload: BranchDiscoveryPayload, target_path: Path) -> dict:
    governance = validate_branches_governance(payload)
    pre_write_hash = sha256_file(target_path)
    yaml_content = branches_to_yaml(payload)

    return {
        "status": "dry_run",
        "target_path": str(target_path),
        "pre_write_hash": pre_write_hash,
        "post_write_hash": None,
        "governance_check": governance,
        "would_write_hash": sha256_text(yaml_content),
    }


def write_branches_raw_with_audit(
    payload: dict,
    target_path: Path,
    audit_log_path: Path,
    approval_token: str,
    caller: str = "api",
    create_backup: bool = True,
    backup_dir: Path | None = None,
) -> dict:
    """Write branches from raw dict, preserving all YAML fields."""
    reject_blank_token(approval_token)

    errors: list[str] = []
    bd = payload.get("branch_discovery", {})
    if bd.get("status") != "completed":
        errors.append("branch_discovery.status must be 'completed'")
    if bd.get("source_snapshot_ref") != "alters/current/snapshot.yaml":
        errors.append("branch_discovery.source_snapshot_ref must be 'alters/current/snapshot.yaml'")
    branch_list = payload.get("branches", [])
    if len(branch_list) != 4:
        errors.append("exactly 4 branches required")
    expected_ids = {"branch_A", "branch_B", "branch_C", "branch_D"}
    actual_ids = {b.get("id") for b in branch_list}
    if actual_ids != expected_ids:
        errors.append(f"branch ids must be {expected_ids}")
    for b in branch_list:
        if not b.get("incompatible_with"):
            errors.append(f"branch {b.get('id')} must have non-empty incompatible_with")
    forbidden_fields = ["alter_generation", "dialogue", "calibration", "archive", "provider", "runtime"]
    for field in forbidden_fields:
        if field in payload:
            errors.append(f"payload must not contain forbidden field: {field}")

    if errors:
        return {
            "status": "rejected",
            "reason": "; ".join(errors),
            "governance_check": {"valid": False, "errors": errors},
        }

    target = Path(target_path)
    token_hash = hash_approval_token(approval_token)
    pre_write_hash = sha256_file(target)

    backup_path = None
    if create_backup and backup_dir:
        backup_path = create_backup_if_exists(target, Path(backup_dir), "branches")

    target.parent.mkdir(parents=True, exist_ok=True)
    io.write_yaml(target, payload)

    post_write_hash = sha256_file(target)

    audit_record = {
        "operation": "branches_raw_persist",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_path": str(target),
        "pre_write_hash": pre_write_hash,
        "post_write_hash": post_write_hash,
        "approval_token_hash": token_hash,
        "caller": caller,
        "rollback_available": backup_path is not None,
        "backup_path": backup_path,
    }

    append_jsonl_audit(audit_log_path, audit_record)

    return {
        "status": "persisted",
        "target_path": str(target),
        "pre_write_hash": pre_write_hash,
        "post_write_hash": post_write_hash,
        "backup_path": backup_path,
        "audit_log_path": str(audit_log_path),
    }


def write_branches_with_audit(
    payload: BranchDiscoveryPayload,
    target_path: Path,
    audit_log_path: Path,
    approval_token: str,
    caller: str = "api",
    create_backup: bool = True,
    backup_dir: Path | None = None,
) -> dict:
    reject_blank_token(approval_token)

    governance = validate_branches_governance(payload)
    if not governance["valid"]:
        return {
            "status": "rejected",
            "reason": "; ".join(governance["errors"]),
            "governance_check": governance,
        }

    target = Path(target_path)
    token_hash = hash_approval_token(approval_token)
    pre_write_hash = sha256_file(target)

    d = {
        "branch_discovery": payload.branch_discovery.model_dump(mode="json"),
        "branches": [b.model_dump(mode="json") for b in payload.branches],
    }

    backup_path = None
    if create_backup and backup_dir:
        backup_path = create_backup_if_exists(target, Path(backup_dir), "branches")

    target.parent.mkdir(parents=True, exist_ok=True)
    io.write_yaml(target, d)

    post_write_hash = sha256_file(target)

    audit_record = {
        "operation": "branches_persist",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_path": str(target),
        "pre_write_hash": pre_write_hash,
        "post_write_hash": post_write_hash,
        "approval_token_hash": token_hash,
        "caller": caller,
        "governance_check": governance,
        "rollback_available": backup_path is not None,
        "backup_path": backup_path,
    }

    append_jsonl_audit(audit_log_path, audit_record)

    return {
        "status": "persisted",
        "target_path": str(target),
        "pre_write_hash": pre_write_hash,
        "post_write_hash": post_write_hash,
        "backup_path": backup_path,
        "audit_log_path": str(audit_log_path),
    }
