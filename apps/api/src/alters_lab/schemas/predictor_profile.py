"""Predictor profile schema — structured baseline predictors."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alters_lab.services.p6_runtime import generate_record_id, utc_now


class TraitBaseline(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conscientiousness: float | None = Field(default=None, ge=0.0, le=1.0)
    neuroticism_negative_emotionality: float | None = Field(default=None, ge=0.0, le=1.0)
    extraversion: float | None = Field(default=None, ge=0.0, le=1.0)
    agreeableness: float | None = Field(default=None, ge=0.0, le=1.0)
    openness: float | None = Field(default=None, ge=0.0, le=1.0)
    source: Literal["short_self_report", "manual_estimate", "unknown"] = "unknown"


class CurrentContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    education_status: str | None = None
    employment_status: str | None = None
    financial_stability: str | None = None
    relationship_status: str | None = None
    health_constraints: list[str] = Field(default_factory=list)


class PredictionTargets(BaseModel):
    model_config = ConfigDict(extra="forbid")

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


class PredictorProfileRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    created_at: str
    updated_at: str | None = None
    source_type: Literal["structured_predictor_profile"] = "structured_predictor_profile"
    self_reported: bool = True
    trait_baseline: TraitBaseline = Field(default_factory=TraitBaseline)
    current_context: CurrentContext = Field(default_factory=CurrentContext)
    prediction_targets: PredictionTargets = Field(default_factory=PredictionTargets)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def auto_fill_ids(cls, data: dict) -> dict:
        if not data.get("profile_id"):
            data["profile_id"] = generate_record_id("pp")
        if not data.get("created_at"):
            data["created_at"] = utc_now()
        return data
