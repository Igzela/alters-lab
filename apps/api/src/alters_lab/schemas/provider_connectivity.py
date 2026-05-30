"""Schemas for provider connectivity check contract."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from alters_lab.schemas.provider_adapter import ProviderMode

ConnectivityStatus = Literal["ok", "skipped", "blocked", "error"]


class ProviderConnectivityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    live_check: bool = False
    confirmation: str | None = None
    timeout_seconds: int | None = None
    dry_run: bool = True


class ProviderConnectivityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ConnectivityStatus
    provider_mode: ProviderMode
    configured: bool
    live_check: bool
    dry_run: bool
    network_call_made: bool
    provider_reachable: bool | None = None
    auth_valid: bool | None = None
    status_code: int | None = None
    latency_ms: int | None = None
    error_type: str | None = None
    message: str
    audit_event_id: str | None = None
    secrets_redacted: Literal[True] = True
    prompt_content_sent: Literal[False] = False
    response_content_persisted: Literal[False] = False
    active_yaml_modified: Literal[False] = False
    rubric_modified: Literal[False] = False
    reality_score_created: Literal[False] = False
    action_alignment_created: Literal[False] = False
    behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False


class ProviderConnectivityAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: uuid4().hex)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider_mode: ProviderMode
    operation: Literal["provider_connectivity_check"] = "provider_connectivity_check"
    status: ConnectivityStatus
    live_check: bool
    dry_run: bool
    network_call_made: bool
    provider_reachable: bool | None = None
    auth_valid: bool | None = None
    status_code: int | None = None
    latency_ms: int | None = None
    error_type: str | None = None
    redacted: Literal[True] = True
    prompt_recorded: Literal[False] = False
    response_recorded: Literal[False] = False
    secret_recorded: Literal[False] = False


class ProviderConnectivityHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    component: Literal["provider-connectivity"] = "provider-connectivity"
    live_network_supported: Literal[True] = True
    live_network_requires_confirmation: Literal[True] = True
    secrets_redacted: Literal[True] = True


class ProviderConnectivityStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_mode: ProviderMode
    configured: bool
    key_configured: bool
    dry_run_default: Literal[True] = True
    live_network_requires_confirmation: Literal[True] = True
    provider_output_persists_by_default: Literal[False] = False
    provider_output_can_write_active_yaml: Literal[False] = False
    provider_output_can_generate_reality_score: Literal[False] = False
    provider_output_can_generate_action_alignment: Literal[False] = False
    behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False
    secrets_redacted: Literal[True] = True
