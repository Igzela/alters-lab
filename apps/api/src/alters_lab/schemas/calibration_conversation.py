"""Schemas for LLM-Driven Calibration conversation and draft extraction."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alters_lab.schemas.calibration_loop import CalibrationScoreValues
from alters_lab.services.p6_runtime import generate_record_id, utc_now


# --- Extraction subsets (what the LLM can extract) ---


class BehaviorMetricsExtract(BaseModel):
    """Subset of WeeklyBehaviorMetricsRecord fields the LLM can extract from conversation."""

    model_config = ConfigDict(extra="forbid")

    week_start: str | None = None
    week_end: str | None = None
    branch_id: str | None = None
    career_education_deep_work_minutes: int | None = Field(default=None, ge=0)
    planned_commitment_follow_through_rate: float | None = Field(
        default=None, ge=0.0, le=1.0
    )
    expense_logged_days: int | None = Field(default=None, ge=0, le=7)
    regular_sleep_nights: int | None = Field(default=None, ge=0, le=7)
    moderate_vigorous_activity_minutes: int | None = Field(default=None, ge=0)
    avoidable_health_risk_events: int | None = Field(default=None, ge=0)
    meaningful_social_contact_count: int | None = Field(default=None, ge=0)
    abandoned_committed_blocks: int | None = Field(default=None, ge=0)
    key_milestone_progress_pct: float | None = Field(default=None, ge=0.0, le=1.0)
    notes: str = ""


class ExternalEvidenceExtract(BaseModel):
    """Single external evidence item the LLM can extract from conversation."""

    model_config = ConfigDict(extra="forbid")

    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    evidence_type: Literal[
        "milestone_completed",
        "exam_or_certification",
        "job_or_market_feedback",
        "project_shipped",
        "income_or_financial_change",
        "health_measurement",
        "relationship_event",
        "user_or_customer_feedback",
        "other",
    ]
    description: str
    objective_strength: Literal["weak", "moderate", "strong"]
    polarity: Literal["positive", "negative", "neutral", "mixed"]
    numeric_value: float | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def require_description(self):
        if not self.description or not self.description.strip():
            raise ValueError("description is required")
        return self


class OutcomeTargetExtract(BaseModel):
    """Single outcome target the LLM can extract from conversation."""

    model_config = ConfigDict(extra="forbid")

    branch_id: str | None = None
    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    horizon_months: int = Field(default=6, ge=1, le=24)
    outcome_name: str
    objective_definition: str
    success_threshold: str
    measurement_method: str
    baseline_value: str | None = None
    target_value: str | None = None
    milestone_id: str | None = None

    @model_validator(mode="after")
    def require_fields(self):
        if not self.objective_definition or not self.objective_definition.strip():
            raise ValueError("objective_definition is required")
        if not self.success_threshold or not self.success_threshold.strip():
            raise ValueError("success_threshold is required")
        return self


class PredictorProfileExtract(BaseModel):
    """Predictor profile data the LLM can extract from conversation."""

    model_config = ConfigDict(extra="forbid")

    conscientiousness: float | None = Field(default=None, ge=0.0, le=1.0)
    neuroticism_negative_emotionality: float | None = Field(
        default=None, ge=0.0, le=1.0
    )
    extraversion: float | None = Field(default=None, ge=0.0, le=1.0)
    agreeableness: float | None = Field(default=None, ge=0.0, le=1.0)
    openness: float | None = Field(default=None, ge=0.0, le=1.0)
    trait_source: Literal["short_self_report", "manual_estimate", "unknown"] = "unknown"
    education_status: str | None = None
    employment_status: str | None = None
    financial_stability: str | None = None
    relationship_status: str | None = None
    health_constraints: list[str] = Field(default_factory=list)
    target_domains: list[
        Literal[
            "career_education",
            "financial",
            "health",
            "relationship",
            "subjective_wellbeing",
        ]
    ] = Field(default_factory=list)
    time_horizon_months: int = Field(default=6, ge=1, le=24)
    limitations: list[str] = Field(default_factory=list)


# --- Draft (the LLM's extraction, pending user confirmation) ---


class CalibrationDraft(BaseModel):
    """A draft extracted by the LLM from conversation, pending user confirmation."""

    model_config = ConfigDict(extra="forbid")

    draft_id: str
    source_type: Literal["llm_calibration_draft"] = "llm_calibration_draft"
    created_at: str
    conversation_id: str
    branch_id: str | None = None
    status: Literal["pending", "confirmed", "rejected"] = "pending"

    # Extracted data (all optional — LLM fills what it can)
    behavior_metrics: BehaviorMetricsExtract | None = None
    rubric_scores: CalibrationScoreValues | None = None
    external_evidence: list[ExternalEvidenceExtract] = Field(default_factory=list)
    outcome_targets: list[OutcomeTargetExtract] = Field(default_factory=list)
    predictor_profile: PredictorProfileExtract | None = None

    # LLM metadata
    llm_model: str | None = None
    extraction_confidence: Literal["high", "medium", "low"] = "low"
    llm_reasoning: str = ""

    # User confirmation
    confirmed_at: str | None = None
    user_corrections: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def auto_fill_ids(cls, data: dict) -> dict:
        if not data.get("draft_id"):
            data["draft_id"] = generate_record_id("cd")
        if not data.get("created_at"):
            data["created_at"] = utc_now()
        return data


# --- Conversation message ---


class ConversationMessage(BaseModel):
    """A single message in a calibration conversation."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str = ""

    @model_validator(mode="before")
    @classmethod
    def auto_fill_timestamp(cls, data: dict) -> dict:
        if not data.get("timestamp"):
            data["timestamp"] = utc_now()
        return data


class CalibrationConversation(BaseModel):
    """A calibration conversation session."""

    model_config = ConfigDict(extra="forbid")

    conversation_id: str
    created_at: str
    branch_id: str | None = None
    status: Literal["active", "completed"] = "active"
    messages: list[ConversationMessage] = Field(default_factory=list)
    draft_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def auto_fill_ids(cls, data: dict) -> dict:
        if not data.get("conversation_id"):
            data["conversation_id"] = generate_record_id("conv")
        if not data.get("created_at"):
            data["created_at"] = utc_now()
        return data


# --- API request/response ---


class StartConversationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: str | None = None


class StartConversationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str
    opening_message: str


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str


class SendMessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str
    reply: str
    draft: CalibrationDraft | None = None


class DraftListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drafts: list[CalibrationDraft]


class ConfirmDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    corrections: dict[str, Any] = Field(default_factory=dict)


class ConfirmDraftResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    draft_id: str
    records_written: list[str]


class RejectDraftResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    draft_id: str
