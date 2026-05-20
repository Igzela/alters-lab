"""P4-M6 Archive Mechanism service.

Archive creation is explicit-only and copies approved source files into a
checkpoint package. Source files are never modified.
"""

from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.schemas.archive_mechanism import (
    ArchiveBoundaryConfirmations,
    ArchiveCreateRequest,
    ArchiveManifestEntry,
    ArchivePackageManifest,
    ArchivePlanRequest,
)
from alters_lab.services.calibration_loop import get_repo_root

ACTIVE_ARCHIVE_SOURCES = [
    "alters/current/snapshot.yaml",
    "alters/current/branches.yaml",
    "alters/current/alters/alter_A.yaml",
    "alters/current/alters/alter_B.yaml",
    "alters/current/alters/alter_C.yaml",
    "alters/current/alters/alter_D.yaml",
    "alters/current/reality_trace.yaml",
    "alters/calibration/rubric.yaml",
]

CALIBRATION_ARCHIVE_GLOBS = [
    "alters/calibration/scores/*.yaml",
    "alters/calibration/rubric_delta_suggestions/*.yaml",
    "alters/calibration/checkpoint_plans/*.yaml",
]


def archive_boundary_confirmations() -> dict:
    return ArchiveBoundaryConfirmations().model_dump()


def archive_root(repo_root: Path | None = None) -> Path:
    root = repo_root or get_repo_root()
    return root / "alters" / "archive" / "checkpoints"


def generate_archive_id() -> str:
    return f"archive_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_type(path: Path) -> str:
    if path.suffix == ".yaml":
        return "yaml"
    return path.suffix.lstrip(".") or "file"


def collect_archive_sources(
    request: ArchivePlanRequest,
    repo_root: Path | None = None,
) -> list[Path]:
    root = repo_root or get_repo_root()
    sources: list[Path] = []
    if request.include_active_yaml:
        sources.extend(root / rel for rel in ACTIVE_ARCHIVE_SOURCES)
    if request.include_calibration_records:
        for pattern in CALIBRATION_ARCHIVE_GLOBS:
            sources.extend(sorted(root.glob(pattern)))
    return [path for path in sources if path.exists() and path.is_file()]


def _entry_for_source(source: Path, root: Path, archive_dir: Path | None = None) -> ArchiveManifestEntry:
    rel = source.relative_to(root)
    archived_path = archive_dir / rel if archive_dir is not None else Path("ARCHIVE_PREVIEW") / rel
    return ArchiveManifestEntry(
        source_path=str(rel),
        archived_path=str(archived_path),
        sha256=sha256_file(source),
        file_type=_file_type(source),
    )


def plan_archive(
    request: ArchivePlanRequest,
    repo_root: Path | None = None,
    archive_id: str | None = None,
) -> ArchivePackageManifest:
    root = repo_root or get_repo_root()
    sources = collect_archive_sources(request, root)
    entries = [_entry_for_source(source, root, None) for source in sources]
    return ArchivePackageManifest(
        archive_id=archive_id or generate_archive_id(),
        status="planned",
        reason=request.reason,
        entries=entries,
        rollback_notes=(
            "Rollback is manual: inspect manifest.yaml, verify sha256 values, "
            "and copy archived files back only after explicit human approval."
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        boundary_confirmations=ArchiveBoundaryConfirmations(),
    )


def create_archive(
    request: ArchiveCreateRequest,
    repo_root: Path | None = None,
) -> tuple[ArchivePackageManifest, Path]:
    root = repo_root or get_repo_root()
    archive_id = generate_archive_id()
    archive_dir = archive_root(root) / archive_id
    archive_dir.mkdir(parents=True, exist_ok=False)

    plan_request = ArchivePlanRequest(
        reason=request.reason,
        include_active_yaml=True,
        include_calibration_records=True,
        caller=request.caller,
    )
    sources = collect_archive_sources(plan_request, root)

    entries: list[ArchiveManifestEntry] = []
    for source in sources:
        rel = source.relative_to(root)
        target = archive_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        entries.append(ArchiveManifestEntry(
            source_path=str(rel),
            archived_path=str(target.relative_to(root)),
            sha256=sha256_file(target),
            file_type=_file_type(source),
        ))

    manifest = ArchivePackageManifest(
        archive_id=archive_id,
        status="created",
        reason=request.reason,
        entries=entries,
        rollback_notes=(
            "Rollback is supported as an explicit manual review workflow only. "
            "This archive operation did not modify source files."
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        boundary_confirmations=ArchiveBoundaryConfirmations(),
    )
    manifest_path = archive_dir / "manifest.yaml"
    manifest_path.write_text(
        yaml.safe_dump(manifest.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return manifest, archive_dir


def list_archives(repo_root: Path | None = None) -> list[dict]:
    root = repo_root or get_repo_root()
    directory = archive_root(root)
    if not directory.exists():
        return []

    archives: list[dict] = []
    for archive_dir in sorted(p for p in directory.glob("archive_*") if p.is_dir()):
        manifest_path = archive_dir / "manifest.yaml"
        if not manifest_path.exists():
            continue
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            continue
        archives.append({
            "archive_id": raw.get("archive_id", archive_dir.name),
            "status": raw.get("status"),
            "created_at": raw.get("created_at"),
            "entry_count": len(raw.get("entries", [])) if isinstance(raw.get("entries"), list) else 0,
            "path": str(archive_dir),
        })
    return archives
