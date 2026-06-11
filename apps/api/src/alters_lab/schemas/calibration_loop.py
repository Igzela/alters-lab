"""Pydantic schemas for P4 calibration loop MVP."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


VALID_BRANCH_IDS = {"branch_A", "branch_B", "branch_C", "branch_D"}
VALID_ALTER_IDS = {"alter_A", "alter_B", "alter_C", "alter_D"}
ALTER_TO_BRANCH = {
    "alter_A": "branch_A",
    "alter_B": "branch_B",
    "alter_C": "branch_C",
    "alter_D": "branch_D",
}


class CalibrationLoopBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active_yaml_modified: bool = False
    rubric_modified: bool = False
    provider_used: bool = False
    frontend_added: bool = False
    database_added: bool = False
    archive_created: bool = False
    regeneration_triggered: bool = False
    promotion_triggered: bool = False
    reality_score_requires_explicit_user_submission: bool = True
    drift_evidence_only: bool = True
    calibration_history_read_only: bool = True


class CalibrationScoreValues(BaseModel):
    model_config = ConfigDict(extra="forbid")

    execution_discipline: int = Field(ge=1, le=5)
    exploration_freedom: int = Field(ge=1, le=5)
    life_state_match: int = Field(ge=1, le=5)
    energy_level: int = Field(ge=1, le=5)


class AlterRubricBaseline(BaseModel):
    """Alter's predicted rubric trajectory."""

    model_config = ConfigDict(extra="forbid")
    alter_id: str
    branch_id: str
    expected_initial: CalibrationScoreValues
    expected_30d: CalibrationScoreValues
    expected_90d: CalibrationScoreValues
    drift_direction: dict[str, str] = Field(default_factory=dict)
    reasoning: str = ""


class CalibrationInputRefs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_ref: str = "alters/current/snapshot.yaml"
    branches_ref: str = "alters/current/branches.yaml"
    alter_ref: str
    rubric_ref: str = "alters/calibration/rubric.yaml"


class RealityScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: str
    alter_id: str
    actual_scores: CalibrationScoreValues
    expected_scores: CalibrationScoreValues | None = None
    user_notes: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    score_id: str | None = None
    submitted_by_user: bool = True
    source: str = "explicit_user_submission"
    caller: str = "api"

    @field_validator("score_id")
    @classmethod
    def validate_score_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("score_id must not be blank")
        if "/" in value or "\\" in value or ".." in value:
            raise ValueError("score_id must not contain path separators")
        if not value.startswith("score_"):
            raise ValueError("score_id must start with score_")
        return value

    @field_validator("user_notes")
    @classmethod
    def validate_user_notes(cls, value: str) -> str:
        if len(value) > 4000:
            raise ValueError("user_notes must be <= 4000 chars")
        return value

    @model_validator(mode="after")
    def validate_branch_alter_pair(self) -> RealityScoreRequest:
        if self.branch_id not in VALID_BRANCH_IDS:
            raise ValueError(f"branch_id must be one of {sorted(VALID_BRANCH_IDS)}")
        if self.alter_id not in VALID_ALTER_IDS:
            raise ValueError(f"alter_id must be one of {sorted(VALID_ALTER_IDS)}")
        expected_branch = ALTER_TO_BRANCH[self.alter_id]
        if self.branch_id != expected_branch:
            raise ValueError(f"alter_id {self.alter_id} belongs to {expected_branch}, not {self.branch_id}")
        return self


class RealityScoreRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    status: str = "recorded"
    created_at: str
    branch_id: str
    alter_id: str
    input_refs: CalibrationInputRefs
    actual_scores: CalibrationScoreValues
    expected_scores: CalibrationScoreValues | None = None
    drift: dict | None = None
    user_notes: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    submitted_by_user: bool = True
    source: str = "explicit_user_submission"
    caller: str = "api"
    boundary_confirmations: CalibrationLoopBoundaryConfirmations = CalibrationLoopBoundaryConfirmations()


class RealityScoreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    record: RealityScoreRecord
    score_path: str
    boundary_confirmations: CalibrationLoopBoundaryConfirmations


class DriftCalculationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actual_scores: CalibrationScoreValues
    expected_scores: CalibrationScoreValues
    branch_id: str | None = None
    alter_id: str | None = None
    score_id: str | None = None


class DriftCalculationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "computed"
    branch_id: str | None = None
    alter_id: str | None = None
    score_id: str | None = None
    per_dimension: dict[str, float]
    overall: float
    checkpoint_threshold: float = 0.6
    threshold_exceeded: bool
    evidence_only: bool = True
    regeneration_triggered: bool = False
    rubric_modified: bool = False
    boundary_confirmations: CalibrationLoopBoundaryConfirmations = CalibrationLoopBoundaryConfirmations()


class CalibrationHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    read_only: bool = True
    records: list[RealityScoreRecord]
    drift_evidence: list[DriftCalculationResult]
    count: int
    boundary_confirmations: CalibrationLoopBoundaryConfirmations


class CalibrationLoopHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "calibration-loop"
    mode: str = "explicit_score_write_drift_evidence_history_read_only"
    provider_used: bool = False
    active_write_allowed: bool = False
    rubric_write_allowed: bool = False
