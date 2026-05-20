"""Pydantic schemas for P5-M1 API Product Surface Hardening."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ProductHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "product-surface"
    read_only: bool = True


class RouteClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    method: str
    classification: str  # "safe" | "internal" | "dangerous"
    tags: list[str] = []


class ProductRoutesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    safe_routes: list[RouteClassification]
    internal_routes: list[RouteClassification]
    dangerous_routes: list[RouteClassification]
    total: int


class ProductStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    phase3_status: str = "sealed_with_notes"
    phase4_status: str = "pass"
    provider_gateway_status: str = "mock_default"
    frontend_availability: str = "available"
    storage_backend: str = "yaml"
    safe_public_endpoints: list[str]
    internal_only_endpoints: list[str]
    no_secrets_exposed: bool = True


class ProductWorkflowCapabilitiesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    capabilities: list[str]
    read_only: bool = True
