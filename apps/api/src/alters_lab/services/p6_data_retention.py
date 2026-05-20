"""P6-M8 data retention/export/delete service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from alters_lab.schemas.p6_data_retention import P6ArchiveRequest, P6DeleteRequest, P6ExportRequest
from alters_lab.services.p6_runtime import (
    P6_RUNTIME_AREAS,
    delete_record,
    generate_record_id,
    list_records,
    read_record,
    redact_secrets,
    utc_now,
    write_record,
)


def build_retention_manifest(repo_root: Path | None = None) -> tuple[list[str], dict[str, int]]:
    areas = sorted(P6_RUNTIME_AREAS)
    counts = {area: len(list_records(area, repo_root)) for area in areas}
    return areas, counts


def export_p6_records(request: P6ExportRequest, repo_root: Path | None = None) -> Path:
    areas = request.areas or sorted(P6_RUNTIME_AREAS)
    _validate_areas(areas)
    payload: dict[str, Any] = {
        "export_id": generate_record_id("p6_export"),
        "created_at": utc_now(),
        "areas": areas,
        "records": {area: redact_secrets(list_records(area, repo_root)) for area in areas if area != "exports"},
        "safety_metadata": {
            "active_yaml_modified": False,
            "secrets_redacted": True,
        },
    }
    path = write_record("exports", payload["export_id"], payload, repo_root)
    return path


def delete_p6_record(request: P6DeleteRequest, repo_root: Path | None = None) -> Path:
    _validate_areas([request.record.area])
    return delete_record(request.record.area, request.record.record_id, repo_root)


def archive_p6_records(request: P6ArchiveRequest, repo_root: Path | None = None) -> Path:
    payload = {
        "archive_id": generate_record_id("p6_archive"),
        "created_at": utc_now(),
        "records": [
            {
                "area": ref.area,
                "record_id": ref.record_id,
                "record": redact_secrets(read_record(ref.area, ref.record_id, repo_root)),
            }
            for ref in request.records
            if _validate_areas([ref.area]) is None
        ],
        "safety_metadata": {
            "active_yaml_modified": False,
            "secrets_redacted": True,
            "archive_is_copy_only": True,
        },
    }
    return write_record("exports", payload["archive_id"], payload, repo_root)


def _validate_areas(areas: list[str]) -> None:
    unknown = [area for area in areas if area not in P6_RUNTIME_AREAS]
    if unknown:
        raise ValueError(f"Unknown P6 runtime area(s): {', '.join(unknown)}")
