"""Draft review and promotion boundary schemas."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, model_validator


class DraftReviewBoundaryConfirmations(BaseModel):
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
    draft_promoted_to_active: bool = False


class DraftReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str
    reviewer: str = "human_owner"
    decision: str
    notes: list[str] = []
    approved_branch_ids: list[str] = []
    approved_alter_ids: list[str] = []
    created_at: str = ""
    boundary_confirmations: DraftReviewBoundaryConfirmations = DraftReviewBoundaryConfirmations()

    @model_validator(mode="after")
    def validate_decision_rules(self) -> DraftReviewDecision:
        allowed = {"approve_for_promotion_package", "request_changes", "reject"}
        if self.decision not in allowed:
            raise ValueError(f"decision must be one of {allowed}")
        if self.decision == "approve_for_promotion_package":
            if not self.approved_branch_ids and not self.approved_alter_ids:
                raise ValueError("approve requires at least one approved_branch_ids or approved_alter_ids")
        if self.decision == "reject":
            if not self.notes:
                raise ValueError("reject requires non-empty notes")
        return self


class DraftReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer: str = "human_owner"
    decision: str
    notes: list[str] = []
    approved_branch_ids: list[str] = []
    approved_alter_ids: list[str] = []
    save_review: bool = False
    approval_token: str | None = None
    caller: str = "api"


class PromotionBranchesPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_discovery: dict
    branches: list[dict]


class PromotionAltersPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alters: list[dict]


class PromotionPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str
    schema_version: int = 1
    status: str = "promotion_candidate"
    review_decision: DraftReviewDecision
    branches_payload: PromotionBranchesPayload | None = None
    alters_payload: PromotionAltersPayload | None = None
    active_write_allowed: bool = False
    requires_controlled_persist_api: bool = True
    target_persist_apis: list[str] = []
    boundary_confirmations: DraftReviewBoundaryConfirmations = DraftReviewBoundaryConfirmations()
    created_at: str = ""

    @model_validator(mode="after")
    def validate_promotion_invariants(self) -> PromotionPackage:
        ALLOWED_APIS = {"/branches/persist", "/alters/persist/{alter_id}", "/alters/persist-batch"}
        if self.active_write_allowed is not False:
            raise ValueError("active_write_allowed must be false")
        if self.requires_controlled_persist_api is not True:
            raise ValueError("requires_controlled_persist_api must be true")
        for api in self.target_persist_apis:
            if api not in ALLOWED_APIS:
                raise ValueError(f"target_persist_api '{api}' not in allowed: {ALLOWED_APIS}")
        return self


class DraftReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    draft_id: str
    review_decision: DraftReviewDecision
    review_path: str | None = None
    promotion_package: PromotionPackage | None = None
    promotion_package_path: str | None = None
    boundary_confirmations: dict


class DraftReviewListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    reviews: list[dict]
    count: int
