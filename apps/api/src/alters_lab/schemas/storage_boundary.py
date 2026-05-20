"""Pydantic schemas for P5-M5 Durable Storage Boundary."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StoragePathClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    access: str  # "read_only" | "write" | "ignored" | "evidence"
    backend: str = "yaml"


class StorageManifestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    default_backend: str = "yaml"
    active_yaml_read_only: list[str]
    calibration_score_write: list[str]
    product_session_write: list[str]
    ignored_runtime_areas: list[str]
    evidence_areas: list[str]
    database_implemented: bool = False
    no_migration: bool = True


class StorageBoundaryHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "storage-boundary"
    default_backend: str = "yaml"
    database_added: bool = False
