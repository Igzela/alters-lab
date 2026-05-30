"""Pydantic schemas for dynamic weight computation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DynamicWeightRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lookback_weeks: int = Field(default=8, ge=2, le=52)


class DimensionWeight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: str
    weight: float = Field(ge=0.5, le=2.0)
    rationale: str


class DynamicWeightResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    weights: list[DimensionWeight]
    overall_alignment: float = Field(ge=0.0, le=1.0)
    recommendation: str
    generated_at: str


class DynamicWeightHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "dynamic-weight"
    mode: str = "evidence_only_advisory"
    provider_used: bool = False
    active_write_allowed: bool = False
    rubric_write_allowed: bool = False
