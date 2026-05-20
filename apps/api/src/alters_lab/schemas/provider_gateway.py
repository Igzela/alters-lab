"""Pydantic schemas for P5-M2 Provider Gateway Boundary."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProviderGatewayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: list[dict]
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int = 800
    caller: str = "api"


class ProviderGatewayResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str  # "mock_response" | "provider_response" | "disabled" | "error"
    mode: str
    model: str
    content: str
    usage: dict | None = None
    redaction_summary: dict = Field(default_factory=dict)
    persisted: bool = False
    active_yaml_modified: bool = False


class ProviderGatewayHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "provider-gateway"
    mode: str
    model: str
    api_key_configured: bool
    no_secrets_exposed: bool = True


class ProviderConfigStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    mode: str
    model: str
    base_url_configured: bool
    api_key_configured: bool
    api_key_value: str = "[redacted]"
    no_secrets_exposed: bool = True
