"""Schemas for unified local app server status."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class LocalAppHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "local-app"
    backend_ready: bool = True


class LocalAppStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    backend_ready: bool
    frontend_available: bool
    frontend_dist_path: str
    runtime_mode: str
    host: str
    port: int
    api_routes_available: bool
    provider_mode: str
    secrets_redacted: bool
    p6_behavior_validated: bool
    p6_sealed: bool
    active_yaml_write_allowed: bool
    rubric_write_allowed: bool


class LocalAppFrontendStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    frontend_available: bool
    frontend_dist_path: str
