"""Controlled Snapshot Write API — persist a confirmed snapshot to disk with governance checks."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from alters_lab.schemas.snapshot import IntakePhase, Snapshot
from alters_lab.services.snapshot_export import snapshot_to_yaml

AUDIT_DIR = Path("docs/harness")
AUDIT_FILE = AUDIT_DIR / "phase3_write_audit.jsonl"

APPROVAL_TOKEN = "p3-001-approved"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    return sha256_text(p.read_text(encoding="utf-8"))


def build_snapshot_persist_payload(snapshot: Snapshot) -> dict:
    return {
        "snapshot": snapshot.model_dump(mode="json"),
        "yaml_content": snapshot_to_yaml(snapshot),
        "built_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_snapshot_persist_governance(snapshot: Snapshot) -> dict:
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


def persist_snapshot_to_disk(
    payload: dict,
    target_path: Path,
    approval_token: str,
) -> dict:
    if approval_token != APPROVAL_TOKEN:
        return {"status": "rejected", "reason": "invalid approval_token"}

    target = Path(target_path)
    sha256_before = sha256_file(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload["yaml_content"], encoding="utf-8")

    sha256_after = sha256_file(target)

    audit_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "snapshot_persist",
        "target_path": str(target),
        "sha256_before": sha256_before,
        "sha256_after": sha256_after,
        "approval_token": approval_token,
    }

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_record) + "\n")

    return {
        "status": "persisted",
        "path": str(target),
        "sha256_before": sha256_before,
        "sha256_after": sha256_after,
        "audit_record": audit_record,
    }
