"""Pydantic schemas for Branch Discovery artifacts."""

from __future__ import annotations

from pydantic import BaseModel, model_validator


class BranchDiscoveryStatus(BaseModel):
    status: str = "not_started"
    source_snapshot_ref: str = ""
    requires_snapshot_phase: str = "completed"
    confirmed_by: str = ""
    confirmation_note: str = ""

    @model_validator(mode="after")
    def validate_completed(self) -> BranchDiscoveryStatus:
        if self.status == "completed":
            if not self.source_snapshot_ref:
                raise ValueError("completed branch_discovery requires source_snapshot_ref")
            if not self.confirmed_by:
                raise ValueError("completed branch_discovery requires confirmed_by")
        return self


class Branch(BaseModel):
    id: str
    label: str
    core_choice: str
    structural_commitment: str
    key_tension_resolved: str
    incompatible_with: list[str]
    preserves: list[str] = []
    sacrifices: list[str] = []
    validation_signal_30d: list[str] = []
    invalid_if: list[str] = []


class BranchDiscoveryPayload(BaseModel):
    branch_discovery: BranchDiscoveryStatus
    branches: list[Branch] = []

    @model_validator(mode="after")
    def validate_branches(self) -> BranchDiscoveryPayload:
        if self.branch_discovery.status == "completed":
            if len(self.branches) != 4:
                raise ValueError("completed branch discovery requires exactly 4 branches")
            expected_ids = {"branch_A", "branch_B", "branch_C", "branch_D"}
            actual_ids = {b.id for b in self.branches}
            if actual_ids != expected_ids:
                raise ValueError(f"branch ids must be {expected_ids}, got {actual_ids}")
            for b in self.branches:
                if not b.incompatible_with:
                    raise ValueError(f"branch {b.id} must have non-empty incompatible_with")
        return self


class BranchesPersistRequest(BaseModel):
    approval_token: str
    branch_discovery: BranchDiscoveryStatus
    branches: list[Branch] = []
    dry_run: bool = False
    caller: str = "api"

    @model_validator(mode="after")
    def validate_approval_token(self) -> BranchesPersistRequest:
        if not self.approval_token or not self.approval_token.strip():
            raise ValueError("approval_token must not be empty or whitespace-only")
        return self

    def to_payload(self) -> BranchDiscoveryPayload:
        return BranchDiscoveryPayload(
            branch_discovery=self.branch_discovery,
            branches=self.branches,
        )


class BranchesPersistResponse(BaseModel):
    status: str
    target_path: str | None
    pre_write_hash: str | None
    post_write_hash: str | None
    audit_log_path: str | None
    backup_path: str | None
    governance_check: dict
    boundary_confirmations: dict
