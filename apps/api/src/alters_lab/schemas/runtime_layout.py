"""Schemas for local runtime layout status."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


RuntimeMode = Literal["dev", "packaged"]


class RuntimeLayoutHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "runtime-layout"
    default_safe: bool = True


class RuntimeLayoutStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    mode: RuntimeMode
    config_path: str
    data_dir: str
    product_data_dir: str
    logs_dir: str
    provider_mode: str
    secrets_storage: str
    secrets_redacted: bool = True
    active_yaml_write_allowed: bool = False
    rubric_write_allowed: bool = False
    provider_output_persists_by_default: bool = False
    provider_output_can_write_active_yaml: bool = False


class RuntimeLayoutEnsureConfigResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    config_path: str
    created_or_exists: bool = True
    secrets_written: bool = False
    runtime_records_written: bool = False
    active_yaml_modified: bool = False
    rubric_modified: bool = False

