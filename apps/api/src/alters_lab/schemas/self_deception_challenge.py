"""P6-M4 self-deception and evidence challenge schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SelfDeceptionRisk = Literal["low", "medium", "high"]
RationalizationPattern = Literal[
    "over_analysis",
    "avoidance_disguised_as_strategy",
    "moral_superiority",
    "productivity_theatre",
    "emotional_minimization",
    "false_urgency",
    "dependency_on_external_validation",
    "other",
]


class SelfDeceptionEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    self_deception_risk: SelfDeceptionRisk
    rationalization_pattern: RationalizationPattern | None = None
    evidence: str | None = None
    avoided_truth: str | None = None
    action_evidence_weak: bool = False
    explanation_contradicts_behavior: bool = False
    existing_strong_challenge_count: int = 0
    save: bool = True
    caller: str = "api"

    @model_validator(mode="after")
    def require_medium_high_fields(self):
        if self.self_deception_risk in ("medium", "high"):
            missing = [
                name
                for name in ("rationalization_pattern", "evidence", "avoided_truth")
                if getattr(self, name) in (None, "")
            ]
            if missing:
                raise ValueError(f"medium/high risk requires: {', '.join(missing)}")
        if self.existing_strong_challenge_count < 0:
            raise ValueError("existing_strong_challenge_count cannot be negative")
        return self


class SelfDeceptionChallengeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    challenge_id: str
    session_id: str
    self_deception_risk: SelfDeceptionRisk
    rationalization_pattern: RationalizationPattern | None = None
    evidence: str | None = None
    avoided_truth: str | None = None
    strong_challenge_allowed: bool
    challenge_level: Literal["none", "gentle", "strong"]
    challenge_text: str | None = None
    created_at: str
    active_yaml_modified: bool = False
    provider_called: bool = False


class EditChallengeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lowered_self_deception_risk: bool = False
    changed_failure_status: bool = False
    lowered_avoidance_level: bool = False
    deleted_negative_facts: list[str] = Field(default_factory=list)


class EditChallengeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    challenge_required: bool
    challenge_question: str | None = None
    triggers: list[str] = Field(default_factory=list)


class SelfDeceptionHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "self-deception-challenge"
    provider_called: bool = False
    active_yaml_modified: bool = False


class SelfDeceptionEvaluateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    record: SelfDeceptionChallengeRecord
    record_path: str | None = None


class SelfDeceptionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    records: list[SelfDeceptionChallengeRecord]
    count: int
