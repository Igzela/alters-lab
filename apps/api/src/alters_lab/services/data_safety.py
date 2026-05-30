"""Data safety and backup helpers for the local app."""

from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from alters_lab.services.runtime_layout import RuntimeLayout

SECRET_CONFIRMATION = "include-secrets-in-backup"
P6_FLAGS = {"behavior_validated": False, "p6_sealed": False}


@dataclass(frozen=True)
class BackupSource:
    section: str
    path: Path
    archive_prefix: str


class DataSafetyError(ValueError):
    """Raised when a data-safety operation is unsafe or invalid."""


def build_user_data_manifest(layout: RuntimeLayout) -> dict[str, Any]:
    paths = {
        "config_path": layout.config_path,
        "secrets_path": layout.secrets_path,
        "data_dir": layout.data_dir,
        "product_data_dir": layout.product_data_dir,
        "logs_dir": layout.logs_dir,
        "exports_dir": layout.product_data_dir / "exports",
    }
    return {
        "status": "ok",
        "runtime_mode": layout.mode,
        "paths": {
            name: {
                "path": str(path),
                "exists": path.exists(),
                "redacted": name == "secrets_path",
            }
            for name, path in paths.items()
        },
        "secrets_redacted": True,
        **P6_FLAGS,
    }


def build_backup_plan(
    layout: RuntimeLayout,
    output_path: Path | None = None,
    include_logs: bool = False,
    include_config: bool = True,
    include_secrets: bool = False,
    confirm_include_secrets: str | None = None,
) -> dict[str, Any]:
    _validate_secret_request(include_secrets, confirm_include_secrets)
    archive_path = output_path or _default_backup_path(layout)
    sources = _backup_sources(layout, include_logs, include_config, include_secrets)
    included_sections = [source.section for source in sources if source.path.exists()]
    missing_sections = [source.section for source in sources if not source.path.exists()]
    excluded_sections = ["secrets"] if not include_secrets else []
    if not include_logs:
        excluded_sections.append("logs")
    if not include_config:
        excluded_sections.append("config")
    return {
        "status": "planned",
        "archive_path": str(archive_path),
        "included_sections": included_sections,
        "missing_sections": missing_sections,
        "excluded_sections": excluded_sections,
        "secrets_included": include_secrets,
        "include_logs": include_logs,
        "include_config": include_config,
        "dry_run": True,
        "manifest": redact_secret_paths(build_user_data_manifest(layout)),
        **P6_FLAGS,
    }


def create_backup_archive(
    layout: RuntimeLayout,
    output_path: Path | None = None,
    include_logs: bool = False,
    include_config: bool = True,
    include_secrets: bool = False,
    confirm_include_secrets: str | None = None,
) -> dict[str, Any]:
    plan = build_backup_plan(
        layout,
        output_path=output_path,
        include_logs=include_logs,
        include_config=include_config,
        include_secrets=include_secrets,
        confirm_include_secrets=confirm_include_secrets,
    )
    archive_path = Path(plan["archive_path"]).expanduser().resolve()
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    sources = _backup_sources(layout, include_logs, include_config, include_secrets)
    with tempfile.TemporaryDirectory(prefix="alters-lab-backup-") as tmp:
        temp_archive = Path(tmp) / archive_path.name
        with tarfile.open(temp_archive, "w:gz") as archive:
            for source in sources:
                if source.path.exists():
                    archive.add(source.path, arcname=source.archive_prefix)
        shutil.move(str(temp_archive), archive_path)
    return {
        **plan,
        "status": "created",
        "archive_path": str(archive_path),
        "dry_run": False,
    }


def verify_no_package_owned_user_paths(package_contents: Iterable[str]) -> dict[str, Any]:
    forbidden = [
        "node_modules",
        ".env",
        ".env.local",
        "alters/product",
        "secrets.yaml",
        ".config/alters-lab",
        ".local/share/alters-lab",
        ".local/state/alters-lab",
        "/logs/",
    ]
    matched = sorted({fragment for line in package_contents for fragment in forbidden if fragment in line})
    return {"status": "PASS" if not matched else "FAIL", "forbidden_matches": matched}


def verify_maintainer_scripts_preserve_user_data(script_paths: Iterable[Path]) -> dict[str, Any]:
    forbidden = ["rm -rf ~/.config", "rm -rf ~/.local", ".config/alters-lab", ".local/share/alters-lab", ".local/state/alters-lab"]
    findings: list[dict[str, str]] = []
    for path in script_paths:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            if token in content:
                findings.append({"path": str(path), "token": token})
    return {"status": "PASS" if not findings else "FAIL", "findings": findings}


def redact_secret_paths(manifest: dict[str, Any]) -> dict[str, Any]:
    redacted = json.loads(json.dumps(manifest))
    paths = redacted.get("paths", {})
    secret = paths.get("secrets_path")
    if isinstance(secret, dict):
        secret["path"] = "[redacted-secret-path]"
        secret["redacted"] = True
    redacted["secrets_redacted"] = True
    return redacted


def _validate_secret_request(include_secrets: bool, confirmation: str | None) -> None:
    if include_secrets and confirmation != SECRET_CONFIRMATION:
        raise DataSafetyError("include_secrets requires confirmation=include-secrets-in-backup")


def _default_backup_path(layout: RuntimeLayout) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return layout.product_data_dir / "exports" / f"alters_lab_backup_{stamp}.tar.gz"


def _backup_sources(
    layout: RuntimeLayout,
    include_logs: bool,
    include_config: bool,
    include_secrets: bool,
) -> list[BackupSource]:
    sources = [BackupSource("data", layout.data_dir, "data")]
    if include_config:
        sources.append(BackupSource("config", layout.config_path, "config/config.yaml"))
    if include_logs:
        sources.append(BackupSource("logs", layout.logs_dir, "logs"))
    if include_secrets:
        sources.append(BackupSource("secrets", layout.secrets_path, "config/secrets.yaml"))
    return sources
