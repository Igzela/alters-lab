"""Schemas for provider-backed dialogue preview contract."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from alters_lab.schemas.provider_adapter import ProviderMode

DialoguePreviewStatus = Literal["ok", "skipped", "blocked", "error"]


class ProviderDialoguePreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: ProviderMode | None = None
    prompt: str = Field(min_length=1)
    system_prompt: str | None = None
    alter_id: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    live_generation: bool = False
    confirmation: str | None = None
    dry_run: bool = True
    persist_output: bool = False
    save_session: bool = False
    caller: str = "provider_dialogue_preview"
    request_id: str | None = None


class ProviderDialoguePreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: DialoguePreviewStatus
    provider_mode: ProviderMode
    configured: bool
    dry_run: bool
    live_generation: bool
    network_call_made: bool
    output_preview: str | None = None
    output_label: Literal["unverified_provider_preview"] = "unverified_provider_preview"
    output_persisted: Literal[False] = False
    save_session: Literal[False] = False
    audit_event_id: str | None = None
    status_code: int | None = None
    latency_ms: int | None = None
    error_type: str | None = None
    message: str
    secrets_redacted: Literal[True] = True
    prompt_persisted: Literal[False] = False
    response_content_persisted: Literal[False] = False
    active_yaml_modified: Literal[False] = False
    rubric_modified: Literal[False] = False
    reality_score_created: Literal[False] = False
    action_alignment_created: Literal[False] = False
    p6_behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False


class ProviderDialoguePreviewAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: uuid4().hex)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider_mode: ProviderMode
    operation: Literal["provider_dialogue_preview"] = "provider_dialogue_preview"
    status: DialoguePreviewStatus
    dry_run: bool
    live_generation: bool
    network_call_made: bool
    output_persisted: Literal[False] = False
    prompt_recorded: Literal[False] = False
    response_recorded: Literal[False] = False
    secret_recorded: Literal[False] = False
    redacted: Literal[True] = True
    status_code: int | None = None
    latency_ms: int | None = None
    error_type: str | None = None


class ProviderDialoguePreviewHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    component: Literal["provider-dialogue-preview"] = "provider-dialogue-preview"
    live_generation_supported: Literal[True] = True
    live_generation_requires_confirmation: Literal[True] = True
    output_persisted_by_default: Literal[False] = False
    secrets_redacted: Literal[True] = True


class ProviderDialoguePreviewStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_mode: ProviderMode
    configured: bool
    dry_run_default: Literal[True] = True
    live_generation_requires_confirmation: Literal[True] = True
    persistence_supported: Literal[False] = False
    provider_output_persists_by_default: Literal[False] = False
    provider_output_can_write_active_yaml: Literal[False] = False
    provider_output_can_generate_reality_score: Literal[False] = False
    provider_output_can_generate_action_alignment: Literal[False] = False
    p6_behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False
    secrets_redacted: Literal[True] = True
