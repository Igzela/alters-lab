"""Shared controlled-write helpers for Phase 3 YAML persistence.

These helpers are used by specific branches/alters services with explicit
target restrictions. They do not provide a generic "write any active YAML" utility.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


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


def reject_blank_token(approval_token: str) -> None:
    if not approval_token or not approval_token.strip():
        raise ValueError("approval_token must be non-empty")


def safe_backup_path(target: Path, backup_dir: Path, prefix: str = "backup") -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return backup_dir / f"{prefix}_{ts}.yaml"


def append_jsonl_audit(audit_log_path: Path, record: dict) -> None:
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def create_backup_if_exists(
    target: Path, backup_dir: Path, prefix: str = "backup"
) -> str | None:
    if target.exists():
        bp = safe_backup_path(target, backup_dir, prefix)
        shutil.copy2(target, bp)
        return str(bp)
    return None
