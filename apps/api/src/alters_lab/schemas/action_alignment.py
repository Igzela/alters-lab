"""P6-M3 action alignment scoring schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

VerdictLabel = Literal[
    "aligned_progress",
    "noisy_progress",
    "avoidance_disguised_as_work",
    "recovery_week",
    "unstable_but_useful",
    "blocked_by_environment",
]


class ActionAlignmentScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    direction_alignment: float = Field(ge=0.0, le=1.0)
    execution_consistency: float = Field(ge=0.0, le=1.0)
    avoidance_level: float = Field(ge=0.0, le=1.0)


class ActionAlignmentEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    one_action_evidence: str
    one_avoidance_or_friction_evidence: str
    one_next_correction: str

    @field_validator("*")
    @classmethod
    def evidence_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("evidence field must not be blank")
        return value.strip()


class ActionAlignmentScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    scores: ActionAlignmentScores
    evidence: ActionAlignmentEvidence
    verdict_label: VerdictLabel
    verdict_sentence: str
    save: bool = True
    caller: str = "api"


class ActionAlignmentScoreRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score_id: str
    session_id: str
    source_type: Literal["weekly_review_session"] = "weekly_review_session"
    derived_from_weekly_review: Literal[True] = True
    scores: ActionAlignmentScores
    action_alignment_score: float
    evidence: ActionAlignmentEvidence
    verdict_label: VerdictLabel
    verdict_sentence: str
    created_at: str
    active_yaml_modified: bool = False
    rubric_modified: bool = False
    provider_called: bool = False


class ActionAlignmentHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "action-alignment"
    provider_called: bool = False
    active_yaml_modified: bool = False


class ActionAlignmentScoreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    score: ActionAlignmentScoreRecord
    score_path: str | None = None


class ActionAlignmentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    scores: list[ActionAlignmentScoreRecord]
    count: int


class ActionAlignmentLoadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    score: ActionAlignmentScoreRecord
