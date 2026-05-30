"""Schemas for hardened provider adapter contract layer."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


ProviderMode = Literal["disabled", "mock", "openai-compatible-http"]
AdapterStatus = Literal["ok", "skipped", "blocked", "error"]


class ProviderAdapterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: ProviderMode
    prompt: str = Field(min_length=1)
    system_prompt: str | None = None
    metadata: dict | None = None
    dry_run: bool = True
    live_check: bool = False
    persist_output: bool = False
    caller: str = "adapter"
    request_id: str | None = None


class ProviderAdapterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AdapterStatus
    provider_ready: bool
    provider_mode: ProviderMode
    dry_run: bool
    live_check: bool
    network_call_made: Literal[False]
    output_preview: str | None = None
    output_persisted: Literal[False] = False
    audit_event_id: str | None = None
    error_type: str | None = None
    message: str
    secrets_redacted: Literal[True] = True
    active_yaml_modified: Literal[False] = False
    rubric_modified: Literal[False] = False
    reality_score_created: Literal[False] = False
    action_alignment_created: Literal[False] = False
    behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False


class ProviderAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: uuid4().hex)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider_mode: ProviderMode
    operation: str
    status: AdapterStatus
    dry_run: bool
    live_check: bool
    network_call_made: Literal[False]
    output_persisted: Literal[False]
    latency_ms: int | None = None
    error_type: str | None = None
    redacted: Literal[True] = True
    prompt_recorded: Literal[False] = False
    response_recorded: Literal[False] = False
    secret_recorded: Literal[False] = False


class ProviderAdapterHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    component: Literal["provider-adapter"] = "provider-adapter"
    real_network_calls_enabled: Literal[False] = False
    secrets_redacted: Literal[True] = True


class ProviderAdapterStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_mode: ProviderMode
    configured: bool
    real_network_calls_enabled: Literal[False] = False
    supported_modes: list[ProviderMode] = Field(
        default_factory=lambda: ["disabled", "mock", "openai-compatible-http"]
    )
    provider_output_persists_by_default: Literal[False] = False
    provider_output_can_write_active_yaml: Literal[False] = False
    provider_output_can_generate_reality_score: Literal[False] = False
    provider_output_can_generate_action_alignment: Literal[False] = False
    behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False
    secrets_redacted: Literal[True] = True
