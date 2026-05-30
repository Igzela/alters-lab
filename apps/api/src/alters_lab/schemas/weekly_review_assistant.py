"""Schemas for weekly review assistant mode.

Provider suggestion is advisory only. User remains the only actor
allowed to submit review content or scores.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from alters_lab.schemas.provider_adapter import ProviderMode

WeeklyReviewAssistantStatus = Literal["ok", "skipped", "blocked", "error"]

RequestedHelp = Literal[
    "summarize_facts",
    "identify_friction",
    "draft_primary_correction",
    "suggest_supporting_actions",
    "challenge_avoidance",
    "general_review_suggestion",
]


class WeeklyReviewAssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weekly_note_record_id: str | None = None
    weekly_review_session_id: str | None = None
    raw_note_excerpt: str | None = None
    review_context: str | None = None
    requested_help: RequestedHelp = "general_review_suggestion"
    dry_run: bool = True
    live_generation: bool = False
    confirmation: str | None = None
    provider_mode: str | None = None
    save_suggestion: bool = False
    caller: str = "weekly_review_assistant"


class WeeklyReviewAssistantResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: WeeklyReviewAssistantStatus
    configured: bool
    suggestion: str | None = None
    suggestion_label: Literal["unverified_provider_suggestion"] = "unverified_provider_suggestion"
    provider_mode: ProviderMode
    dry_run: bool
    live_generation: bool
    network_call_made: bool
    suggestion_persisted: Literal[False] = False
    weekly_review_completed: Literal[False] = False
    action_alignment_created: Literal[False] = False
    reality_score_created: Literal[False] = False
    active_yaml_modified: Literal[False] = False
    rubric_modified: Literal[False] = False
    behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False
    secrets_redacted: Literal[True] = True
    prompt_persisted: Literal[False] = False
    response_content_persisted: Literal[False] = False
    audit_event_id: str | None = None
    status_code: int | None = None
    latency_ms: int | None = None
    error_type: str | None = None
    message: str


class WeeklyReviewAssistantAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: uuid4().hex)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider_mode: ProviderMode
    operation: Literal["weekly_review_assistant"] = "weekly_review_assistant"
    status: WeeklyReviewAssistantStatus
    dry_run: bool
    live_generation: bool
    network_call_made: bool
    suggestion_persisted: Literal[False] = False
    prompt_recorded: Literal[False] = False
    response_recorded: Literal[False] = False
    secret_recorded: Literal[False] = False
    redacted: Literal[True] = True
    status_code: int | None = None
    latency_ms: int | None = None
    error_type: str | None = None


class WeeklyReviewAssistantHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    component: Literal["weekly-review-assistant"] = "weekly-review-assistant"
    live_generation_supported: Literal[True] = True
    live_generation_requires_confirmation: Literal[True] = True
    output_persisted_by_default: Literal[False] = False
    secrets_redacted: Literal[True] = True


class WeeklyReviewAssistantStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_mode: ProviderMode
    configured: bool
    dry_run_default: Literal[True] = True
    live_generation_requires_confirmation: Literal[True] = True
    suggestion_persistence_supported: Literal[False] = False
    provider_output_persists_by_default: Literal[False] = False
    provider_output_can_write_active_yaml: Literal[False] = False
    provider_output_can_generate_reality_score: Literal[False] = False
    provider_output_can_generate_action_alignment: Literal[False] = False
    behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False
    secrets_redacted: Literal[True] = True
