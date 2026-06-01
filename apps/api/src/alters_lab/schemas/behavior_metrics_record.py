"""Weekly behavior metrics record schema."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

MissingReason = Literal[
    "not_tracked",
    "not_applicable",
    "device_failure",
    "user_skipped",
    "unknown",
]

SourceQuality = Literal["manual", "mixed", "device_assisted"]


class WeeklyBehaviorMetricsRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    source_type: Literal["weekly_behavior_metrics"] = "weekly_behavior_metrics"

    week_start: date
    week_end: date

    branch_id: str | None = None
    milestone_id: str | None = None
    milestone_observable_evidence: str | None = None

    career_education_deep_work_minutes: int = Field(default=0, ge=0)
    planned_commitment_follow_through_rate: float = Field(
        default=0.0, ge=0.0, le=1.0
    )
    expense_logged_days: int = Field(default=0, ge=0, le=7)
    regular_sleep_nights: int = Field(default=0, ge=0, le=7)
    moderate_vigorous_activity_minutes: int = Field(default=0, ge=0)
    avoidable_health_risk_events: int = Field(default=0, ge=0)
    meaningful_social_contact_count: int = Field(default=0, ge=0)
    abandoned_committed_blocks: int = Field(default=0, ge=0)
    key_milestone_progress_pct: float = Field(default=0.0, ge=0.0, le=1.0)

    missing_metrics: dict[str, MissingReason] = Field(default_factory=dict)
    source_quality: SourceQuality = "manual"
    notes: str = ""

    @model_validator(mode="after")
    def validate_milestone_evidence(self):
        if self.key_milestone_progress_pct > 0:
            if not self.milestone_id:
                raise ValueError(
                    "milestone_id required when key_milestone_progress_pct > 0"
                )
            if (
                not self.milestone_observable_evidence
                or not self.milestone_observable_evidence.strip()
            ):
                raise ValueError(
                    "milestone_observable_evidence required when key_milestone_progress_pct > 0"
                )
        return self


def validate_missing_metric_ids(
    record: WeeklyBehaviorMetricsRecord,
    known_metric_ids: frozenset[str],
) -> None:
    unknown = set(record.missing_metrics) - known_metric_ids
    if unknown:
        raise ValueError(f"unknown missing metric ids: {sorted(unknown)}")


def get_metric_value_for_analysis(
    record: WeeklyBehaviorMetricsRecord, metric_id: str
) -> float | int | None:
    if metric_id in record.missing_metrics:
        return None

    from alters_lab.schemas.behavior_metrics_catalog import METRIC_ID_TO_FIELD

    try:
        field_name = METRIC_ID_TO_FIELD[metric_id]
    except KeyError as exc:
        raise ValueError(f"unknown metric id: {metric_id}") from exc

    return getattr(record, field_name)
