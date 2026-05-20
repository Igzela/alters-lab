"""Pydantic schemas for P4-M6 Archive Mechanism."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ArchiveBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    explicit_archive_request: bool = True
    active_yaml_modified: bool = False
    rubric_modified: bool = False
    provider_used: bool = False
    frontend_added: bool = False
    database_added: bool = False
    regeneration_triggered: bool = False
    rollback_supported: bool = True


class ArchiveManifestEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_path: str
    archived_path: str
    sha256: str
    file_type: str


class ArchivePackageManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    archive_id: str
    status: Literal["planned", "created"]
    reason: str
    entries: list[ArchiveManifestEntry]
    rollback_notes: str
    created_at: str
    boundary_confirmations: ArchiveBoundaryConfirmations


class ArchivePlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    include_active_yaml: bool = True
    include_calibration_records: bool = True
    caller: str = "api"

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("reason must be non-empty")
        if len(value) > 1000:
            raise ValueError("reason must be <= 1000 chars")
        return value


class ArchiveCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    caller: str = "api"

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("reason must be non-empty")
        if len(value) > 1000:
            raise ValueError("reason must be <= 1000 chars")
        return value


class ArchiveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["planned", "created", "rejected"]
    manifest: ArchivePackageManifest
    archive_path: str | None
    boundary_confirmations: dict


class ArchiveListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    archives: list[dict]
    count: int
    boundary_confirmations: dict


class ArchiveHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "archive-mechanism"
    mode: str = "explicit_archive_copy_only"
    provider_used: bool = False
    active_write_allowed: bool = False
    regeneration_triggered: bool = False
