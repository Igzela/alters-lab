"""Pydantic schemas for Alter artifacts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class AlterSourceRefs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot_ref: str = ""
    branches_ref: str = ""
    rubric_ref: str = ""


class AlterQualityStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    human_confirmed: bool = False
    active: bool = False
    notes: list[str] = []


class AlterVoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    core_stance: str = ""
    typical_concern: str = ""
    decision_style: str = ""
    self_warning: str = ""


class AlterPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    branch_ref: str
    label: str = ""
    source_refs: AlterSourceRefs = AlterSourceRefs()
    quality_status: AlterQualityStatus = AlterQualityStatus()
    voice: AlterVoice = AlterVoice()

    @model_validator(mode="after")
    def validate_required_fields(self) -> AlterPayload:
        if self.id not in ("alter_A", "alter_B", "alter_C", "alter_D"):
            raise ValueError(f"alter id must be one of alter_A-D, got {self.id}")
        expected_branch = self.id.replace("alter_", "branch_")
        if self.branch_ref != expected_branch:
            raise ValueError(f"branch_ref must be {expected_branch}, got {self.branch_ref}")
        if self.source_refs.snapshot_ref != "alters/current/snapshot.yaml":
            raise ValueError("source_refs.snapshot_ref must be 'alters/current/snapshot.yaml'")
        if self.source_refs.branches_ref != "alters/current/branches.yaml":
            raise ValueError("source_refs.branches_ref must be 'alters/current/branches.yaml'")
        if self.source_refs.rubric_ref != "alters/calibration/rubric.yaml":
            raise ValueError("source_refs.rubric_ref must be 'alters/calibration/rubric.yaml'")
        if not self.quality_status.human_confirmed:
            raise ValueError("quality_status.human_confirmed must be true")
        if not self.quality_status.active:
            raise ValueError("quality_status.active must be true")
        if not self.voice.core_stance:
            raise ValueError("voice.core_stance must be non-empty")
        return self


class AlterPersistRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approval_token: str
    id: str = ""
    branch_ref: str = ""
    label: str = ""
    source_refs: AlterSourceRefs = AlterSourceRefs()
    quality_status: AlterQualityStatus = AlterQualityStatus()
    voice: AlterVoice = AlterVoice()
    dry_run: bool = False
    caller: str = "api"

    @model_validator(mode="after")
    def validate_approval_token(self) -> AlterPersistRequest:
        if not self.approval_token or not self.approval_token.strip():
            raise ValueError("approval_token must not be empty or whitespace-only")
        return self

    def to_payload(self) -> AlterPayload:
        return AlterPayload(
            id=self.id,
            branch_ref=self.branch_ref,
            label=self.label,
            source_refs=self.source_refs,
            quality_status=self.quality_status,
            voice=self.voice,
        )


class AlterPersistResponse(BaseModel):
    status: str
    target_path: str | None
    pre_write_hash: str | None
    post_write_hash: str | None
    audit_log_path: str | None
    backup_path: str | None
    governance_check: dict
    boundary_confirmations: dict


class AlterBatchPersistRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approval_token: str
    alters: list[AlterPayload]
    dry_run: bool = False
    caller: str = "api"

    @model_validator(mode="after")
    def validate_approval_token(self) -> AlterBatchPersistRequest:
        if not self.approval_token or not self.approval_token.strip():
            raise ValueError("approval_token must not be empty or whitespace-only")
        return self

    @model_validator(mode="after")
    def validate_alter_ids(self) -> AlterBatchPersistRequest:
        expected = {"alter_A", "alter_B", "alter_C", "alter_D"}
        actual = {a.id for a in self.alters}
        if actual != expected:
            raise ValueError(f"batch must include exactly {expected}, got {actual}")
        return self


class AlterBatchPersistResponse(BaseModel):
    status: str
    written_paths: list[str]
    pre_write_hashes: dict
    post_write_hashes: dict
    audit_log_path: str | None
    governance_check: dict
    boundary_confirmations: dict
