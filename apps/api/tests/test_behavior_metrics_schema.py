"""Tests for behavior metrics schemas."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from alters_lab.schemas.behavior_metrics_catalog import (
    METRIC_ID_TO_FIELD,
    load_catalog,
    load_known_metric_ids,
)
from alters_lab.schemas.behavior_metrics_record import (
    WeeklyBehaviorMetricsRecord,
    get_metric_value_for_analysis,
    validate_missing_metric_ids,
)


def _make_catalog_yaml(tmp_path: Path) -> Path:
    catalog_dir = tmp_path / "alters" / "product" / "behavior_metrics" / "catalog"
    catalog_dir.mkdir(parents=True)
    catalog = {
        "behavior_metric_set": {
            "id": "test_set",
            "version": "0.1",
            "created_at": "2026-01-01T00:00:00Z",
            "metrics": [
                {"id": "career_education_deep_work_minutes", "domain": "career", "label": "Deep Work", "unit": "minutes", "aggregation": "sum"},
                {"id": "financial_planfulness", "domain": "financial", "label": "Expense Days", "unit": "days", "aggregation": "sum"},
                {"id": "key_milestone_progress", "domain": "milestone", "label": "Milestone", "unit": "ratio", "aggregation": "last"},
            ],
        }
    }
    path = catalog_dir / "test_catalog.yaml"
    path.write_text(yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8")
    return path


# --- Phase 1 tests ---


def test_valid_weekly_record():
    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_test_001",
        week_start="2026-05-25",
        week_end="2026-05-31",
        career_education_deep_work_minutes=120,
        planned_commitment_follow_through_rate=0.8,
        expense_logged_days=5,
        regular_sleep_nights=6,
        moderate_vigorous_activity_minutes=90,
        avoidable_health_risk_events=0,
        meaningful_social_contact_count=3,
        abandoned_committed_blocks=1,
    )
    assert record.record_id == "wr_test_001"
    assert record.career_education_deep_work_minutes == 120


def test_unknown_field_rejected():
    with pytest.raises(ValidationError, match="extra"):
        WeeklyBehaviorMetricsRecord(
            record_id="wr_test_002",
            week_start="2026-05-25",
            week_end="2026-05-31",
            unknown_field="bad",
        )


def test_negative_numeric_rejected():
    with pytest.raises(ValidationError):
        WeeklyBehaviorMetricsRecord(
            record_id="wr_test_003",
            week_start="2026-05-25",
            week_end="2026-05-31",
            career_education_deep_work_minutes=-10,
        )


def test_ratio_out_of_range_rejected():
    with pytest.raises(ValidationError):
        WeeklyBehaviorMetricsRecord(
            record_id="wr_test_004",
            week_start="2026-05-25",
            week_end="2026-05-31",
            planned_commitment_follow_through_rate=1.5,
        )


def test_milestone_progress_requires_milestone_id():
    with pytest.raises(ValidationError, match="milestone_id required"):
        WeeklyBehaviorMetricsRecord(
            record_id="wr_test_005",
            week_start="2026-05-25",
            week_end="2026-05-31",
            key_milestone_progress_pct=0.5,
        )


def test_milestone_progress_requires_evidence():
    with pytest.raises(ValidationError, match="milestone_observable_evidence required"):
        WeeklyBehaviorMetricsRecord(
            record_id="wr_test_006",
            week_start="2026-05-25",
            week_end="2026-05-31",
            key_milestone_progress_pct=0.5,
            milestone_id="ms_001",
        )


def test_missing_metrics_supports_known_reasons():
    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_test_007",
        week_start="2026-05-25",
        week_end="2026-05-31",
        missing_metrics={
            "career_education_deep_work_minutes": "device_failure",
            "sleep_regular_nights": "user_skipped",
        },
    )
    assert record.missing_metrics["career_education_deep_work_minutes"] == "device_failure"


def test_get_metric_value_returns_none_when_missing():
    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_test_008",
        week_start="2026-05-25",
        week_end="2026-05-31",
        regular_sleep_nights=5,
        missing_metrics={"sleep_regular_nights": "user_skipped"},
    )
    assert get_metric_value_for_analysis(record, "sleep_regular_nights") is None


def test_financial_planfulness_maps_to_expense_logged_days():
    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_test_009",
        week_start="2026-05-25",
        week_end="2026-05-31",
        expense_logged_days=4,
    )
    assert get_metric_value_for_analysis(record, "financial_planfulness") == 4


def test_key_milestone_progress_maps_to_pct():
    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_test_010",
        week_start="2026-05-25",
        week_end="2026-05-31",
        key_milestone_progress_pct=0.6,
        milestone_id="ms_001",
        milestone_observable_evidence="shipped feature X",
    )
    assert get_metric_value_for_analysis(record, "key_milestone_progress") == 0.6


def test_load_known_metric_ids(tmp_path: Path):
    path = _make_catalog_yaml(tmp_path)
    ids = load_known_metric_ids(path)
    assert "career_education_deep_work_minutes" in ids
    assert "financial_planfulness" in ids
    assert len(ids) == 3


def test_validate_missing_metric_ids_catches_unknown(tmp_path: Path):
    path = _make_catalog_yaml(tmp_path)
    known_ids = load_known_metric_ids(path)
    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_test_011",
        week_start="2026-05-25",
        week_end="2026-05-31",
        missing_metrics={"nonexistent_metric": "not_tracked"},
    )
    with pytest.raises(ValueError, match="unknown missing metric ids"):
        validate_missing_metric_ids(record, known_ids)
