"""Tests for behavior metrics API endpoints."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    response = client.get("/behavior-metrics/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["component"] == "behavior-metrics"
    assert data["provider_required"] is False


def test_catalog():
    response = client.get("/behavior-metrics/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "behavior_metric_set" in data
    metrics = data["behavior_metric_set"]["metrics"]
    assert len(metrics) == 9
    ids = [m["id"] for m in metrics]
    assert "career_education_deep_work_minutes" in ids
    assert "key_milestone_progress" in ids


def test_create_and_get_weekly_record(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        "alters_lab.services.p6_runtime.get_repo_root", lambda: tmp_path
    )
    # Also patch the catalog path resolver in behavior_metrics service
    monkeypatch.setattr(
        "alters_lab.services.behavior_metrics._resolve_catalog_path",
        lambda root: None if root is None else (
            root / "alters" / "product" / "behavior_metrics" / "catalog" / "behavior_metric_set_v0_2.yaml"
        ),
    )
    # Write a minimal catalog so build_weekly_record can validate
    catalog_dir = tmp_path / "alters" / "product" / "behavior_metrics" / "catalog"
    catalog_dir.mkdir(parents=True)
    catalog = {
        "behavior_metric_set": {
            "id": "test", "version": "0.1", "created_at": "2026-01-01T00:00:00Z",
            "metrics": [
                {"id": "career_education_deep_work_minutes", "domain": "c", "label": "DW", "unit": "min", "aggregation": "sum"},
            ],
        }
    }
    (catalog_dir / "behavior_metric_set_v0_2.yaml").write_text(
        yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
    )

    payload = {
        "record_id": "wr_api_001",
        "week_start": "2026-05-25",
        "week_end": "2026-05-31",
        "career_education_deep_work_minutes": 150,
        "planned_commitment_follow_through_rate": 0.9,
        "expense_logged_days": 6,
        "regular_sleep_nights": 5,
    }
    response = client.post("/behavior-metrics/weekly-records", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "saved"
    assert data["record"]["career_education_deep_work_minutes"] == 150

    get_resp = client.get("/behavior-metrics/weekly-records/wr_api_001")
    assert get_resp.status_code == 200
    assert get_resp.json()["record"]["record_id"] == "wr_api_001"


def test_list_weekly_records():
    response = client.get("/behavior-metrics/weekly-records")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "records" in data
    assert "count" in data


def test_invalid_ratio_rejected():
    payload = {
        "record_id": "wr_api_bad",
        "week_start": "2026-05-25",
        "week_end": "2026-05-31",
        "planned_commitment_follow_through_rate": 1.5,
    }
    response = client.post("/behavior-metrics/weekly-records", json=payload)
    assert response.status_code == 422 or response.status_code == 400


def test_get_nonexistent_record():
    response = client.get("/behavior-metrics/weekly-records/nonexistent")
    assert response.status_code == 404
