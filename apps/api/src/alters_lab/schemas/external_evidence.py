"""External evidence schema — observed real-world outcomes."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alters_lab.services.p6_runtime import generate_record_id, utc_now

_DOMAINS = Literal[
    "career_education",
    "financial",
    "health",
    "relationship",
    "subjective_wellbeing",
]

_EVIDENCE_TYPES = Literal[
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


class ExternalEvidenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    source_type: Literal["external_evidence"] = "external_evidence"
    branch_id: str | None = None
    target_id: str | None = None
    snapshot_id: str | None = None
    domain: _DOMAINS
    evidence_type: _EVIDENCE_TYPES
    observed_at: str
    description: str
    objective_strength: Literal["weak", "moderate", "strong"]
    polarity: Literal["positive", "negative", "neutral", "mixed"]
    numeric_value: float | None = None
    unit: str | None = None
    artifact_ref: str | None = None
    notes: str = ""

    @model_validator(mode="before")
    @classmethod
    def auto_fill_ids(cls, data: dict) -> dict:
        if not data.get("evidence_id"):
            data["evidence_id"] = generate_record_id("ee")
        if not data.get("observed_at"):
            data["observed_at"] = utc_now()
        return data

    @model_validator(mode="after")
    def require_description(self):
        if not self.description or not self.description.strip():
            raise ValueError("description is required")
        return self
