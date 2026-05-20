"""P6-M5 alter recommendation schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from alters_lab.schemas.obsidian_weekly_note import SessionType
from alters_lab.schemas.self_deception_challenge import SelfDeceptionRisk


class AlterRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_type: SessionType
    unresolved_drift_alter_ids: list[str] = Field(default_factory=list)
    overused_alter_ids: list[str] = Field(default_factory=list)
    decision_conflict_high: bool = False
    self_deception_risk: SelfDeceptionRisk = "low"
    repeated_failure_same_category: bool = False
    user_requests_deeper_review: bool = False
    save: bool = True
    caller: str = "api"


class AlterFactorScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_type_match: float
    unresolved_drift_match: float
    challenge_value: float
    action_alignment_relevance: float
    overuse_penalty: float
    total: float


class AlterRecommendationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendation_id: str
    session_type: SessionType
    primary_alter_id: str
    counter_alter_id: str | None = None
    counter_alter_reason: str | None = None
    factor_scores: dict[str, AlterFactorScores]
    override_alter_id: str | None = None
    override_reason: str | None = None
    created_at: str
    active_yaml_modified: bool = False
    provider_called: bool = False


class AlterOverrideRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    override_alter_id: str
    reason: str
    caller: str = "api"

    @field_validator("reason")
    @classmethod
    def reason_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("override reason is required")
        return value.strip()


class AlterRecommendationHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "alter-recommendation"
    provider_called: bool = False
    active_yaml_modified: bool = False


class AlterRecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    recommendation: AlterRecommendationRecord
    recommendation_path: str | None = None


class AlterRecommendationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    recommendations: list[AlterRecommendationRecord]
    count: int
