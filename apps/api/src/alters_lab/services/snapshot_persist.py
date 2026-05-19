"""Controlled Snapshot Write API — persist a confirmed snapshot to disk with governance checks."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from alters_lab.schemas.snapshot import Snapshot
from alters_lab.services.snapshot_export import snapshot_to_yaml


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    return sha256_text(p.read_text(encoding="utf-8"))


def hash_approval_token(approval_token: str) -> str:
    if not approval_token or not approval_token.strip():
        raise ValueError("approval_token must be non-empty")
    return sha256_text(approval_token)


def build_snapshot_persist_payload(snapshot: Snapshot) -> dict:
    return {
        "snapshot": snapshot.model_dump(mode="json"),
        "yaml_content": snapshot_to_yaml(snapshot),
        "built_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_snapshot_persist_governance(snapshot: Snapshot) -> dict:
    from alters_lab.schemas.snapshot import IntakePhase

    errors: list[str] = []

    if snapshot.intake_status.phase != IntakePhase.completed:
        errors.append("intake_status.phase must be 'completed'")

    if snapshot.intake_status.pending_anchor is not None:
        errors.append("intake_status.pending_anchor must be None")

    if not snapshot.anchors.heaviest_constraint:
        errors.append("anchors.heaviest_constraint must be non-empty")
    if not snapshot.anchors.most_unclear:
        errors.append("anchors.most_unclear must be non-empty")
    if not snapshot.anchors.unwilling_to_give_up:
        errors.append("anchors.unwilling_to_give_up must be non-empty")

    if snapshot.evidence_policy.source_mode != "human_provided":
        errors.append("evidence_policy.source_mode must be 'human_provided'")

    if getattr(snapshot, "branch_discovery", None) is not None:
        errors.append("snapshot must not have branch_discovery trigger")

    return {"valid": len(errors) == 0, "errors": errors}


def preview_snapshot_persist(snapshot: Snapshot, target_path: Path) -> dict:
    governance = validate_snapshot_persist_governance(snapshot)
    pre_write_hash = sha256_file(target_path)
    payload = build_snapshot_persist_payload(snapshot)

    return {
        "status": "dry_run",
        "target_path": str(target_path),
        "pre_write_hash": pre_write_hash,
        "post_write_hash": None,
        "governance_check": governance,
        "would_write_hash": sha256_text(payload["yaml_content"]),
    }


def write_snapshot_with_audit(
    snapshot: Snapshot,
    target_path: Path,
    audit_log_path: Path,
    approval_token: str,
    caller: str = "api",
    create_backup: bool = True,
    backup_dir: Path | None = None,
) -> dict:
    if not approval_token or not approval_token.strip():
        raise ValueError("approval_token must be non-empty")

    governance = validate_snapshot_persist_governance(snapshot)
    if not governance["valid"]:
        return {
            "status": "rejected",
            "reason": "; ".join(governance["errors"]),
            "governance_check": governance,
        }

    target = Path(target_path)
    audit = Path(audit_log_path)
    token_hash = hash_approval_token(approval_token)

    pre_write_hash = sha256_file(target)

    payload = build_snapshot_persist_payload(snapshot)

    backup_path = None
    if create_backup and target.exists():
        if backup_dir:
            bp = Path(backup_dir)
        else:
            bp = audit.parent / "backups" / "phase3"
        bp.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_file = bp / f"snapshot_{ts}.yaml"
        shutil.copy2(target, backup_file)
        backup_path = str(backup_file)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload["yaml_content"], encoding="utf-8")

    post_write_hash = sha256_file(target)

    audit_record = {
        "operation": "snapshot_persist",
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

    audit.parent.mkdir(parents=True, exist_ok=True)
    with open(audit, "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_record) + "\n")

    return {
        "status": "persisted",
        "target_path": str(target),
        "pre_write_hash": pre_write_hash,
        "post_write_hash": post_write_hash,
        "backup_path": backup_path,
        "audit_log_path": str(audit),
    }
