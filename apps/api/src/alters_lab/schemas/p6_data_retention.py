"""P6-M8 data retention/export/delete schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class P6RecordRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    area: str
    record_id: str


class P6RetentionHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "p6-data-retention"
    active_yaml_modified: bool = False
    provider_called: bool = False


class P6RetentionManifestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    runtime_areas: list[str]
    record_counts: dict[str, int]
    default_long_term_save: bool = True
    manual_delete_supported: bool = True
    export_supported: bool = True
    archive_supported: bool = True
    active_yaml_modified: bool = False


class P6ExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    areas: list[str] = Field(default_factory=list)
    caller: str = "api"


class P6DeleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record: P6RecordRef
    confirmation: str
    caller: str = "api"

    @field_validator("confirmation")
    @classmethod
    def confirmation_required(cls, value: str) -> str:
        if value != "delete":
            raise ValueError("confirmation must be 'delete'")
        return value


class P6ArchiveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: list[P6RecordRef]
    confirmation: str
    caller: str = "api"

    @field_validator("confirmation")
    @classmethod
    def confirmation_required(cls, value: str) -> str:
        if value != "archive":
            raise ValueError("confirmation must be 'archive'")
        return value


class P6RetentionActionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    path: str | None = None
    deleted_record: P6RecordRef | None = None
    active_yaml_modified: bool = False
    secrets_redacted: bool = True
