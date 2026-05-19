"""Pydantic schemas for Generation Draft Runtime."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class GenerationSourceRefs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_ref: str = "alters/current/snapshot.yaml"
    branches_ref: str | None = "alters/current/branches.yaml"
    alters_ref: str | None = "alters/current/alters"
    rubric_ref: str | None = "alters/calibration/rubric.yaml"


class GenerationBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_only: bool = True
    active_yaml_modified: bool = False
    snapshot_yaml_modified: bool = False
    branches_yaml_modified: bool = False
    alters_modified: bool = False
    value_alignment_modified: bool = False
    dialogue_modified: bool = False
    reality_trace_modified: bool = False
    calibration_score_created: bool = False
    drift_computed: bool = False
    archive_created: bool = False
    provider_used: bool = False
    frontend_added: bool = False
    database_added: bool = False
    active_persist_triggered: bool = False
    generation_promoted_to_active: bool = False


class DraftGeneratorInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str = "deterministic_template"
    provider_used: bool = False
    deterministic: bool = True
    version: str = "1.0"


class BranchDraftCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    core_choice: str
    structural_commitment: str
    key_tension_resolved: str
    incompatible_with: list[str]
    source_reasoning: list[str]
    draft_status: str = "candidate"
    requires_human_review: bool = True


class AlterDraftCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    branch_ref: str
    label: str
    source_refs: GenerationSourceRefs = GenerationSourceRefs()
    quality_status: dict = {"human_confirmed": False, "active": False}
    voice: dict = {}
    draft_status: str = "candidate"
    requires_human_review: bool = True


class GenerationDraftPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str
    schema_version: int = 1
    draft_type: str
    status: str = "draft"
    generator: DraftGeneratorInfo = DraftGeneratorInfo()
    source_refs: GenerationSourceRefs = GenerationSourceRefs()
    branch_drafts: list[BranchDraftCandidate] = []
    alter_drafts: list[AlterDraftCandidate] = []
    human_review_required: bool = True
    active_write_allowed: bool = False
    created_at: str = ""
    boundary_confirmations: GenerationBoundaryConfirmations = GenerationBoundaryConfirmations()

    @model_validator(mode="after")
    def validate_draft_type(self) -> GenerationDraftPackage:
        allowed = {"branches", "alters", "cycle_package"}
        if self.draft_type not in allowed:
            raise ValueError(f"draft_type must be one of {allowed}, got {self.draft_type}")
        if self.active_write_allowed:
            raise ValueError("active_write_allowed must be false")
        if not self.human_review_required:
            raise ValueError("human_review_required must be true")
        return self


class GenerationPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = "active_yaml_chain"
    include_branches: bool = True
    include_alters: bool = True
    save_draft: bool = False
    approval_token: str | None = None
    caller: str = "api"

    @model_validator(mode="after")
    def validate_save_draft(self) -> GenerationPreviewRequest:
        if self.save_draft and not self.approval_token:
            raise ValueError("approval_token required when save_draft=true")
        return self


class GenerationPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    draft_package: GenerationDraftPackage
    draft_path: str | None = None
    audit_log_path: str | None = None
    governance_check: dict = {"valid": True, "errors": []}
    boundary_confirmations: dict = {}


class DraftListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    drafts: list[dict] = []
    count: int = 0
