"""Tests for behavior metric trend analysis."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml

from alters_lab.schemas.behavior_metrics_record import WeeklyBehaviorMetricsRecord
from alters_lab.schemas.behavior_metric_trend import BehaviorMetricTrendRequest
from alters_lab.services.behavior_metric_trend import analyze_behavior_trends
from alters_lab.services.behavior_metrics import save_weekly_record


def _setup_catalog(tmp_path: Path) -> None:
    catalog_dir = tmp_path / "alters" / "product" / "behavior_metrics" / "catalog"
    catalog_dir.mkdir(parents=True)
    catalog = {
        "behavior_metric_set": {
            "id": "test_set",
            "version": "0.1",
            "created_at": "2026-01-01T00:00:00Z",
            "metrics": [
                {"id": "career_education_deep_work_minutes", "domain": "career", "label": "DW", "unit": "min", "aggregation": "sum"},
                {"id": "financial_planfulness", "domain": "fin", "label": "EL", "unit": "days", "aggregation": "sum"},
                {"id": "key_milestone_progress", "domain": "ms", "label": "MP", "unit": "ratio", "aggregation": "last"},
            ],
        }
    }
    (catalog_dir / "behavior_metric_set_v0_2.yaml").write_text(
        yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
    )


def _write_records(tmp_path: Path, metric: str, values: list[int | float]) -> None:
    today = date.today()
    for i, val in enumerate(values):
        week_start = today - timedelta(weeks=len(values) - i)
        week_end = week_start + timedelta(days=6)
        data: dict = {
            "record_id": f"wr_{i:03d}",
            "source_type": "weekly_behavior_metrics",
            "week_start": str(week_start),
            "week_end": str(week_end),
            "career_education_deep_work_minutes": 0,
            "planned_commitment_follow_through_rate": 0.0,
            "expense_logged_days": 0,
            "regular_sleep_nights": 0,
            "moderate_vigorous_activity_minutes": 0,
            "avoidable_health_risk_events": 0,
            "meaningful_social_contact_count": 0,
            "abandoned_committed_blocks": 0,
            "key_milestone_progress_pct": 0.0,
            "missing_metrics": {},
            "source_quality": "manual",
            "notes": "",
        }
        if metric == "career_education_deep_work_minutes":
            data["career_education_deep_work_minutes"] = val
        elif metric == "financial_planfulness":
            data["expense_logged_days"] = val
        elif metric == "key_milestone_progress":
            data["key_milestone_progress_pct"] = val
            data["milestone_id"] = "ms_001"
            data["milestone_observable_evidence"] = "evidence"

        area_dir = tmp_path / "alters" / "product" / "behavior_metrics" / "weekly_records"
        area_dir.mkdir(parents=True, exist_ok=True)
        (area_dir / f"wr_{i:03d}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )


def test_missing_metric_excluded(tmp_path: Path):
    _setup_catalog(tmp_path)
    _write_records(tmp_path, "career_education_deep_work_minutes", [100, 120, 0, 150])
    # Mark one as missing
    area_dir = tmp_path / "alters" / "product" / "behavior_metrics" / "weekly_records"
    data = yaml.safe_load((area_dir / "wr_001.yaml").read_text(encoding="utf-8"))
    data["missing_metrics"] = {"career_education_deep_work_minutes": "user_skipped"}
    (area_dir / "wr_001.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
    )

    request = BehaviorMetricTrendRequest(lookback_weeks=8)
    result = analyze_behavior_trends(request, repo_root=tmp_path)
    career_trend = next(
        t for t in result.trends if t.metric_id == "career_education_deep_work_minutes"
    )
    # Only 3 valid points (skipped one)
    assert career_trend.data_points == 3


def test_insufficient_data(tmp_path: Path):
    _setup_catalog(tmp_path)
    _write_records(tmp_path, "career_education_deep_work_minutes", [100])

    request = BehaviorMetricTrendRequest(lookback_weeks=8)
    result = analyze_behavior_trends(request, repo_root=tmp_path)
    career_trend = next(
        t for t in result.trends if t.metric_id == "career_education_deep_work_minutes"
    )
    assert career_trend.direction == "insufficient_data"
    assert career_trend.data_points == 1


def test_financial_planfulness_uses_expense_logged_days(tmp_path: Path):
    _setup_catalog(tmp_path)
    _write_records(tmp_path, "financial_planfulness", [3, 5, 4, 6])

    request = BehaviorMetricTrendRequest(lookback_weeks=8)
    result = analyze_behavior_trends(request, repo_root=tmp_path)
    fin_trend = next(t for t in result.trends if t.metric_id == "financial_planfulness")
    assert fin_trend.data_points == 4
    assert fin_trend.current_value == 6


def test_key_milestone_progress_uses_pct(tmp_path: Path):
    _setup_catalog(tmp_path)
    _write_records(tmp_path, "key_milestone_progress", [0.2, 0.4, 0.6, 0.8])

    request = BehaviorMetricTrendRequest(lookback_weeks=8)
    result = analyze_behavior_trends(request, repo_root=tmp_path)
    ms_trend = next(t for t in result.trends if t.metric_id == "key_milestone_progress")
    assert ms_trend.current_value == 0.8
    assert ms_trend.direction == "improving"


def test_route_b_placeholders(tmp_path: Path):
    _setup_catalog(tmp_path)
    _write_records(tmp_path, "career_education_deep_work_minutes", [100, 120, 130, 140])

    request = BehaviorMetricTrendRequest(lookback_weeks=8)
    result = analyze_behavior_trends(request, repo_root=tmp_path)
    trend = result.trends[0]
    assert trend.population_percentile is None
    assert trend.deviation_from_baseline is None
    assert trend.route_a_available is True
    assert trend.route_b_available is False


def test_no_life_score(tmp_path: Path):
    _setup_catalog(tmp_path)
    _write_records(tmp_path, "career_education_deep_work_minutes", [100, 120, 130, 140])

    request = BehaviorMetricTrendRequest(lookback_weeks=8)
    result = analyze_behavior_trends(request, repo_root=tmp_path)
    result_dict = result.model_dump()
    assert "life_score" not in result_dict
    for trend in result_dict["trends"]:
        assert "life_score" not in trend
