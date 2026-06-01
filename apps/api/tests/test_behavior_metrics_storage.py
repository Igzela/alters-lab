"""Tests for behavior metrics storage service."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from alters_lab.schemas.behavior_metrics_record import WeeklyBehaviorMetricsRecord
from alters_lab.services.behavior_metrics import (
    build_weekly_record,
    list_weekly_records,
    load_weekly_record,
    save_weekly_record,
)


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
            ],
        }
    }
    (catalog_dir / "behavior_metric_set_v0_2.yaml").write_text(
        yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
    )


def _make_record(record_id: str = "wr_001") -> WeeklyBehaviorMetricsRecord:
    return WeeklyBehaviorMetricsRecord(
        record_id=record_id,
        week_start="2026-05-25",
        week_end="2026-05-31",
        career_education_deep_work_minutes=100,
    )


def test_save_and_load(tmp_path: Path):
    _setup_catalog(tmp_path)
    record = _make_record()
    build_weekly_record(record, repo_root=tmp_path)
    path = save_weekly_record(record, repo_root=tmp_path)
    assert path.exists()

    loaded = load_weekly_record("wr_001", repo_root=tmp_path)
    assert loaded.record_id == "wr_001"
    assert loaded.career_education_deep_work_minutes == 100


def test_list_records(tmp_path: Path):
    _setup_catalog(tmp_path)
    for i in range(3):
        record = _make_record(f"wr_{i:03d}")
        save_weekly_record(record, repo_root=tmp_path)

    records = list_weekly_records(repo_root=tmp_path)
    assert len(records) == 3


def test_load_nonexistent_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_weekly_record("nonexistent", repo_root=tmp_path)
