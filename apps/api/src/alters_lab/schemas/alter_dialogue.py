"""Pydantic schemas for Alter Dialogue Runtime (P4-M1)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator


class AlterDialogueBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")
    read_only: bool = True
    active_yaml_modified: bool = False
    dialogue_persisted_to_active: bool = False
    provider_used: bool = False
    provider_config_added: bool = False
    frontend_added: bool = False
    database_added: bool = False
    controlled_persist_called: bool = False
    live_execution_called: bool = False
    reality_score_created: bool = False
    drift_computed: bool = False
    calibration_modified: bool = False
    archive_created: bool = False


class AlterDialogueContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alter_id: str
    branch_ref: str
    label: str
    core_stance: str
    typical_concern: str = ""
    decision_style: str = ""
    self_warning: str = ""
    source_refs: dict
    quality_status: dict
    allowed_scope: list[str]
    forbidden_scope: list[str]


class AlterDialogueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_message: str
    include_context_packet: bool = True
    caller: str = "api"

    @field_validator("user_message")
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("user_message must be non-empty")
        if len(v) > 4000:
            raise ValueError("user_message must be <= 4000 chars")
        return v


class AlterDialoguePromptPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alter_id: str
    system_instruction: str
    user_message: str
    full_alter_yaml: dict
    full_context_injected: bool = True
    context_summary: dict
    safety_boundaries: list[str]
    style_constraints: list[str]
    context_injection_policy: str = "full_alter_yaml_required"
    persistence_policy: str = "read_only_no_active_yaml_write"
    provider_ready: bool = False


class AlterDialogueResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str  # context_ready | prompt_packet_ready | rejected
    alter_id: str
    dialogue_context: AlterDialogueContext | None = None
    prompt_packet: AlterDialoguePromptPacket | None = None
    boundary_confirmations: dict


class AlterDialogueHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    component: str = "alter-dialogue"
    mode: str = "read_only_no_provider"
    provider_used: bool = False
    active_write_allowed: bool = False


class AlterDialogueListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    alters: list[dict]
    count: int
    boundary_confirmations: dict
