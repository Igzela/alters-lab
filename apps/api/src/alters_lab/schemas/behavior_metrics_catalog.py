"""Behavior metrics catalog schema and loader."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict


class BehaviorMetricDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    domain: str
    label: str
    unit: str
    aggregation: str
    description: str = ""


class BehaviorMetricSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    version: str
    created_at: str
    description: str = ""
    metrics: list[BehaviorMetricDefinition]


class BehaviorMetricCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    behavior_metric_set: BehaviorMetricSet


DEFAULT_CATALOG_PATH = (
    Path(__file__).resolve().parents[5]
    / "alters"
    / "product"
    / "behavior_metrics"
    / "catalog"
    / "behavior_metric_set_v0_2.yaml"
)


def load_catalog(catalog_path: Path | None = None) -> BehaviorMetricCatalog:
    path = catalog_path or DEFAULT_CATALOG_PATH
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return BehaviorMetricCatalog(**data)


def load_known_metric_ids(catalog_path: Path | None = None) -> frozenset[str]:
    catalog = load_catalog(catalog_path)
    return frozenset(m.id for m in catalog.behavior_metric_set.metrics)


METRIC_ID_TO_FIELD: dict[str, str] = {
    "career_education_deep_work_minutes": "career_education_deep_work_minutes",
    "planned_commitment_follow_through_rate": "planned_commitment_follow_through_rate",
    "financial_planfulness": "expense_logged_days",
    "sleep_regular_nights": "regular_sleep_nights",
    "moderate_vigorous_activity_minutes": "moderate_vigorous_activity_minutes",
    "avoidable_health_risk_events": "avoidable_health_risk_events",
    "meaningful_social_contact_count": "meaningful_social_contact_count",
    "abandoned_committed_blocks": "abandoned_committed_blocks",
    "key_milestone_progress": "key_milestone_progress_pct",
}
