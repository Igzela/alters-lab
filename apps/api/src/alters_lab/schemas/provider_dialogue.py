"""Pydantic schemas for P5-M3 Provider-backed Alter Dialogue."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProviderDialogueBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active_yaml_modified: bool = False
    rubric_modified: bool = False
    reality_score_created: bool = False
    drift_computed: bool = False
    archive_triggered: bool = False
    checkpoint_triggered: bool = False
    persisted: bool = False
    no_secrets_in_session: bool = True


class ProviderDialogueReplyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_message: str
    provider_mode_override: str | None = None  # only "mock" | "disabled" allowed in tests
    save_session: bool = False
    caller: str = "api"


class ProviderDialogueReplyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    alter_id: str
    reply_text: str
    provider_metadata: dict = Field(default_factory=dict)
    prompt_packet_summary: dict = Field(default_factory=dict)
    safety_boundaries: ProviderDialogueBoundaryConfirmations = Field(
        default_factory=ProviderDialogueBoundaryConfirmations
    )
    persisted: bool = False
    session_path: str | None = None
    boundary_confirmations: ProviderDialogueBoundaryConfirmations = Field(
        default_factory=ProviderDialogueBoundaryConfirmations
    )


class ProviderDialogueHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "provider-dialogue"
    provider_mode: str
    available_alters: list[str]
    default_persist: bool = False
