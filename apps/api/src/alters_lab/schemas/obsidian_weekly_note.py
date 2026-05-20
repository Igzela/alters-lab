"""P6-M1 Obsidian weekly note ingest schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SessionType = Literal["personal", "project", "learning", "relationship"]


class WeeklyNoteBoundaryConfirmations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_note_preserved: bool = True
    derived_from_raw_note: bool = True
    active_yaml_modified: bool = False
    rubric_modified: bool = False
    provider_called: bool = False
    reality_score_created: bool = False
    alter_recommendation_created: bool = False


class WeeklyNoteRawInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_note: str
    source_path: str | None = None
    save: bool = True
    caller: str = "api"

    @field_validator("raw_note")
    @classmethod
    def raw_note_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("raw_note must not be blank")
        return value


class WeeklyNoteSectionParse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_type_raw: str
    observable_facts_raw: list[str]
    subjective_state_raw: str
    primary_problem_raw: str
    friction_or_avoidance_point_raw: str
    desired_correction_raw: str
    warnings: list[str] = Field(default_factory=list)


class WeeklyNoteEditDiff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    changed_fields: list[str] = Field(default_factory=list)
    deleted_facts: list[str] = Field(default_factory=list)
    deleted_negative_facts: list[str] = Field(default_factory=list)
    challenge_required: bool = False
    challenge_question: str | None = None
    correction_note: str
    edited_at: str


class WeeklyNoteExtractedRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    source_type: Literal["obsidian_weekly_note"] = "obsidian_weekly_note"
    raw_note_preserved: Literal[True] = True
    derived_from_raw_note: Literal[True] = True
    source_path: str | None = None
    raw_note: str
    session_type: SessionType
    observable_facts: list[str] = Field(min_length=5, max_length=7)
    subjective_state: str
    primary_problem: str
    friction_or_avoidance_point: str
    desired_correction: str
    extraction_warnings: list[str] = Field(default_factory=list)
    edit_history: list[WeeklyNoteEditDiff] = Field(default_factory=list)
    created_at: str
    updated_at: str | None = None

    @field_validator(
        "subjective_state",
        "primary_problem",
        "friction_or_avoidance_point",
        "desired_correction",
    )
    @classmethod
    def text_fields_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be blank")
        return value.strip()


class WeeklyNoteEditPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_type: SessionType | None = None
    observable_facts: list[str] | None = Field(default=None, min_length=5, max_length=7)
    subjective_state: str | None = None
    primary_problem: str | None = None
    friction_or_avoidance_point: str | None = None
    desired_correction: str | None = None
    correction_note: str
    caller: str = "api"

    @field_validator("correction_note")
    @classmethod
    def correction_note_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("correction_note is required")
        return value.strip()


class WeeklyNoteIngestRequest(WeeklyNoteRawInput):
    pass


class WeeklyNoteIngestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    record: WeeklyNoteExtractedRecord
    record_path: str | None = None
    boundary_confirmations: WeeklyNoteBoundaryConfirmations = Field(
        default_factory=WeeklyNoteBoundaryConfirmations
    )


class WeeklyNoteListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    records: list[WeeklyNoteExtractedRecord]
    count: int


class WeeklyNoteLoadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    record: WeeklyNoteExtractedRecord


class WeeklyNoteEditResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    record: WeeklyNoteExtractedRecord
    diff: WeeklyNoteEditDiff
    record_path: str | None = None


class WeeklyNoteHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "obsidian-weekly-note"
    provider_called: bool = False
    active_yaml_modified: bool = False


class WeeklyNoteEditChallengeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diff: WeeklyNoteEditDiff

    @model_validator(mode="after")
    def diff_must_have_change(self):
        if not self.diff.changed_fields:
            raise ValueError("diff must include at least one changed field")
        return self
