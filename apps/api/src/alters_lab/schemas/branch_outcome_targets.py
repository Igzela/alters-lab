"""Branch outcome target schema — objective externally verifiable targets."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alters_lab.services.p6_runtime import generate_record_id, utc_now

_STATUS_TRANSITIONS = {
    "planned": {"active", "abandoned"},
    "active": {"achieved", "missed", "abandoned"},
    "achieved": set(),
    "missed": set(),
    "abandoned": set(),
}


class BranchOutcomeTargetRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_id: str
    branch_id: str
    milestone_id: str | None = None
    domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    horizon_months: int = Field(ge=1, le=24)
    outcome_name: str
    objective_definition: str
    success_threshold: str
    measurement_method: str
    baseline_value: str | None = None
    target_value: str | None = None
    created_at: str
    status: Literal["planned", "active", "achieved", "missed", "abandoned"] = "planned"
    final_observed_value: str | None = None
    evaluated_at: str | None = None

    @model_validator(mode="before")
    @classmethod
    def auto_fill_ids(cls, data: dict) -> dict:
        if not data.get("target_id"):
            data["target_id"] = generate_record_id("bot")
        if not data.get("created_at"):
            data["created_at"] = utc_now()
        if not data.get("objective_definition"):
            raise ValueError("objective_definition is required")
        if not data.get("success_threshold"):
            raise ValueError("success_threshold is required")
        return data

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in _STATUS_TRANSITIONS.get(self.status, set())


def evaluate_target(
    record: BranchOutcomeTargetRecord,
    final_observed_value: str,
    achieved: bool,
) -> BranchOutcomeTargetRecord:
    """Create an evaluated copy of the target."""
    data = record.model_dump(mode="json")
    data["final_observed_value"] = final_observed_value
    data["evaluated_at"] = utc_now()
    data["status"] = "achieved" if achieved else "missed"
    return BranchOutcomeTargetRecord(**data)
