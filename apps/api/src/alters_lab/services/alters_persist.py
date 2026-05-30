"""Controlled Alter Write API — persist confirmed alter artifacts to disk."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from alters_lab.schemas.alters import AlterBatchPersistRequest, AlterPayload
from alters_lab.services import io
from alters_lab.services.controlled_write import (
    append_jsonl_audit,
    create_backup_if_exists,
    hash_approval_token,
    reject_blank_token,
    sha256_file,
    sha256_text,
)

VALID_ALTER_IDS = {"alter_A", "alter_B", "alter_C", "alter_D"}


def alter_to_yaml(alter: AlterPayload) -> str:
    d = alter.model_dump(mode="json")
    return io.dump_yaml_str(d)


def validate_alter_governance(alter: AlterPayload) -> dict:
    errors: list[str] = []

    if alter.id not in VALID_ALTER_IDS:
        errors.append(f"alter id must be one of {VALID_ALTER_IDS}")

    expected_branch = alter.id.replace("alter_", "branch_")
    if alter.branch_ref != expected_branch:
        errors.append(f"branch_ref must be {expected_branch}")

    if alter.source_refs.snapshot_ref != "alters/current/snapshot.yaml":
        errors.append("source_refs.snapshot_ref must be 'alters/current/snapshot.yaml'")
    if alter.source_refs.branches_ref != "alters/current/branches.yaml":
        errors.append("source_refs.branches_ref must be 'alters/current/branches.yaml'")
    if alter.source_refs.rubric_ref != "alters/calibration/rubric.yaml":
        errors.append("source_refs.rubric_ref must be 'alters/calibration/rubric.yaml'")

    if not alter.quality_status.human_confirmed:
        errors.append("quality_status.human_confirmed must be true")
    if not alter.quality_status.active:
        errors.append("quality_status.active must be true")

    if not alter.voice.core_stance:
        errors.append("voice.core_stance must be non-empty")

    forbidden_fields = ["dialogue", "calibration_scoring", "drift", "archive", "provider", "database", "frontend", "generation"]
    for field in forbidden_fields:
        if field in alter.model_fields_set:
            errors.append(f"alter must not contain forbidden field: {field}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_batch_governance(alters: list[AlterPayload]) -> dict:
    all_errors: list[str] = []
    for alter in alters:
        result = validate_alter_governance(alter)
        if not result["valid"]:
            all_errors.extend(result["errors"])

    return {"valid": len(all_errors) == 0, "errors": all_errors}


def get_alter_target_path(alter_id: str, base_dir: Path) -> Path:
    return base_dir / f"{alter_id}.yaml"


def preview_alter_persist(alter: AlterPayload, target_path: Path) -> dict:
    governance = validate_alter_governance(alter)
    pre_write_hash = sha256_file(target_path)
    yaml_content = alter_to_yaml(alter)

    return {
        "status": "dry_run",
        "target_path": str(target_path),
        "pre_write_hash": pre_write_hash,
        "post_write_hash": None,
        "governance_check": governance,
        "would_write_hash": sha256_text(yaml_content),
    }


def write_alter_with_audit(
    alter: AlterPayload,
    target_path: Path,
    audit_log_path: Path,
    approval_token: str,
    caller: str = "api",
    create_backup: bool = True,
    backup_dir: Path | None = None,
) -> dict:
    reject_blank_token(approval_token)

    governance = validate_alter_governance(alter)
    if not governance["valid"]:
        return {
            "status": "rejected",
            "reason": "; ".join(governance["errors"]),
            "governance_check": governance,
        }

    target = Path(target_path)
    token_hash = hash_approval_token(approval_token)
    pre_write_hash = sha256_file(target)

    backup_path = None
    if create_backup and backup_dir:
        backup_path = create_backup_if_exists(target, Path(backup_dir), alter.id)

    target.parent.mkdir(parents=True, exist_ok=True)
    io.write_yaml(target, alter.model_dump(mode="json"))

    post_write_hash = sha256_file(target)

    audit_record = {
        "operation": "alter_persist",
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


def validate_alter_raw_dict(alter: dict) -> dict:
    """Validate required fields on a raw alter dict without Pydantic model."""
    errors: list[str] = []
    alter_id = alter.get("id", "")
    if alter_id not in VALID_ALTER_IDS:
        errors.append(f"alter id must be one of {VALID_ALTER_IDS}")
    expected_branch = alter_id.replace("alter_", "branch_")
    if alter.get("branch_ref") != expected_branch:
        errors.append(f"branch_ref must be {expected_branch}")
    src = alter.get("source_refs", {})
    if src.get("snapshot_ref") != "alters/current/snapshot.yaml":
        errors.append("source_refs.snapshot_ref must be 'alters/current/snapshot.yaml'")
    if src.get("branches_ref") != "alters/current/branches.yaml":
        errors.append("source_refs.branches_ref must be 'alters/current/branches.yaml'")
    if src.get("rubric_ref") != "alters/calibration/rubric.yaml":
        errors.append("source_refs.rubric_ref must be 'alters/calibration/rubric.yaml'")
    qs = alter.get("quality_status", {})
    if qs.get("human_confirmed") is not True:
        errors.append("quality_status.human_confirmed must be true")
    if qs.get("active") is not True:
        errors.append("quality_status.active must be true")
    voice = alter.get("voice", {})
    if not voice.get("core_stance"):
        errors.append("voice.core_stance must be non-empty")
    forbidden_fields = ["dialogue", "calibration_scoring", "drift", "archive", "provider", "database", "frontend", "generation"]
    for field in forbidden_fields:
        if field in alter:
            errors.append(f"alter must not contain forbidden field: {field}")
    return {"valid": len(errors) == 0, "errors": errors}


def write_alter_raw_batch_with_audit(
    alters: list[dict],
    base_dir: Path,
    audit_log_path: Path,
    approval_token: str,
    caller: str = "api",
    create_backup: bool = True,
    backup_dir: Path | None = None,
) -> dict:
    """Write alter batch from raw dicts, preserving all YAML fields."""
    reject_blank_token(approval_token)

    all_errors: list[str] = []
    for a in alters:
        result = validate_alter_raw_dict(a)
        if not result["valid"]:
            all_errors.extend(result["errors"])
    if all_errors:
        return {
            "status": "rejected",
            "reason": "; ".join(all_errors),
            "governance_check": {"valid": False, "errors": all_errors},
        }

    token_hash = hash_approval_token(approval_token)
    pre_write_hashes: dict[str, str] = {}
    post_write_hashes: dict[str, str] = {}
    written_paths: list[str] = []
    backup_paths: list[str] = []

    for alter in alters:
        alter_id = alter["id"]
        target = get_alter_target_path(alter_id, base_dir)
        pre_write_hashes[alter_id] = sha256_file(target)

        if create_backup and backup_dir:
            bp = create_backup_if_exists(target, Path(backup_dir), alter_id)
            if bp:
                backup_paths.append(bp)

        target.parent.mkdir(parents=True, exist_ok=True)
        io.write_yaml(target, alter)

        post_write_hashes[alter_id] = sha256_file(target)
        written_paths.append(str(target))

    audit_record = {
        "operation": "alters_raw_batch_persist",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "written_paths": written_paths,
        "pre_write_hashes": pre_write_hashes,
        "post_write_hashes": post_write_hashes,
        "approval_token_hash": token_hash,
        "caller": caller,
        "rollback_available": len(backup_paths) > 0,
        "backup_paths": backup_paths,
    }

    append_jsonl_audit(audit_log_path, audit_record)

    return {
        "status": "persisted",
        "written_paths": written_paths,
        "pre_write_hashes": pre_write_hashes,
        "post_write_hashes": post_write_hashes,
        "backup_paths": backup_paths,
        "audit_log_path": str(audit_log_path),
    }


def write_alter_batch_with_audit(
    alters: list[AlterPayload],
    base_dir: Path,
    audit_log_path: Path,
    approval_token: str,
    caller: str = "api",
    create_backup: bool = True,
    backup_dir: Path | None = None,
) -> dict:
    reject_blank_token(approval_token)

    governance = validate_batch_governance(alters)
    if not governance["valid"]:
        return {
            "status": "rejected",
            "reason": "; ".join(governance["errors"]),
            "governance_check": governance,
        }

    token_hash = hash_approval_token(approval_token)
    pre_write_hashes = {}
    post_write_hashes = {}
    written_paths = []
    backup_paths = []

    for alter in alters:
        target = get_alter_target_path(alter.id, base_dir)
        pre_write_hashes[alter.id] = sha256_file(target)

        if create_backup and backup_dir:
            bp = create_backup_if_exists(target, Path(backup_dir), alter.id)
            if bp:
                backup_paths.append(bp)

        target.parent.mkdir(parents=True, exist_ok=True)
        io.write_yaml(target, alter.model_dump(mode="json"))

        post_write_hashes[alter.id] = sha256_file(target)
        written_paths.append(str(target))

    audit_record = {
        "operation": "alters_batch_persist",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "written_paths": written_paths,
        "pre_write_hashes": pre_write_hashes,
        "post_write_hashes": post_write_hashes,
        "approval_token_hash": token_hash,
        "caller": caller,
        "governance_check": governance,
        "rollback_available": len(backup_paths) > 0,
        "backup_paths": backup_paths,
    }

    append_jsonl_audit(audit_log_path, audit_record)

    return {
        "status": "persisted",
        "written_paths": written_paths,
        "pre_write_hashes": pre_write_hashes,
        "post_write_hashes": post_write_hashes,
        "backup_paths": backup_paths,
        "audit_log_path": str(audit_log_path),
    }
