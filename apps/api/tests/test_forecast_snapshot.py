"""Tests for forecast snapshot schema, service, and API."""

from __future__ import annotations

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from pydantic import ValidationError

from alters_lab.schemas.forecast_snapshot import ForecastSnapshotRecord, ForecastSummarySnapshot
from alters_lab.services.forecast_snapshot import save_snapshot, load_snapshot, list_snapshots


def _valid_summary(**overrides) -> dict:
    base = {
        "trajectory_direction": "improving",
        "confidence": "medium",
        "credibility": "medium",
        "explanation": "test explanation",
    }
    base.update(overrides)
    return base


def _valid_snapshot(**overrides) -> dict:
    base = {
        "branch_id": "branch_A",
        "horizon_months": 3,
        "forecast_payload": {"key": "value"},
        "forecast_summary": _valid_summary(),
        "route_a_summary": {"available": True},
        "route_b_summary": {"available": False},
        "calibration_divergence_summary": {"divergence_status": "insufficient_data"},
        "limitations": ["test limitation"],
    }
    base.update(overrides)
    return base


# --- Schema tests ---

def test_valid_snapshot_creates():
    record = ForecastSnapshotRecord(**_valid_snapshot())
    assert record.snapshot_id.startswith("fs_")
    assert record.source_type == "forecast_snapshot"
    assert record.locked is True
    assert record.branch_id == "branch_A"


def test_snapshot_no_life_score():
    data = _valid_snapshot()
    record = ForecastSnapshotRecord(**data)
    dumped = record.model_dump(mode="json")
    assert "life_score" not in str(dumped).lower()


def test_snapshot_locked_by_default():
    record = ForecastSnapshotRecord(**_valid_snapshot())
    assert record.locked is True


def test_snapshot_custom_id():
    record = ForecastSnapshotRecord(**_valid_snapshot(snapshot_id="fs_custom_123"))
    assert record.snapshot_id == "fs_custom_123"


def test_snapshot_invalid_direction():
    with pytest.raises(ValidationError):
        ForecastSummarySnapshot(
            trajectory_direction="invalid",
            confidence="low",
            credibility="low",
            explanation="test",
        )


def test_snapshot_extra_fields_rejected():
    with pytest.raises(ValidationError):
        ForecastSnapshotRecord(**_valid_snapshot(bad_field="nope"))


# --- Service tests ---

def test_save_and_load_snapshot(tmp_path: Path):
    record = ForecastSnapshotRecord(**_valid_snapshot())
    path = save_snapshot(record, repo_root=tmp_path)
    assert path.exists()
    loaded = load_snapshot(record.snapshot_id, repo_root=tmp_path)
    assert loaded.snapshot_id == record.snapshot_id
    assert loaded.branch_id == "branch_A"
    assert loaded.locked is True


def test_list_snapshots(tmp_path: Path):
    for bid in ["branch_A", "branch_B"]:
        record = ForecastSnapshotRecord(**_valid_snapshot(branch_id=bid))
        save_snapshot(record, repo_root=tmp_path)
    snapshots = list_snapshots(repo_root=tmp_path)
    assert len(snapshots) == 2
    assert {s.branch_id for s in snapshots} == {"branch_A", "branch_B"}


def test_snapshot_preserves_forecast_payload(tmp_path: Path):
    payload = {"branch_id": "branch_A", "generated_at": "2025-01-01T00:00:00Z"}
    record = ForecastSnapshotRecord(**_valid_snapshot(forecast_payload=payload))
    save_snapshot(record, repo_root=tmp_path)
    loaded = load_snapshot(record.snapshot_id, repo_root=tmp_path)
    assert loaded.forecast_payload == payload


# --- API tests ---

@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


def _forecast_result_payload() -> dict:
    return {
        "branch_id": "branch_A",
        "generated_at": "2025-01-01T00:00:00Z",
        "horizon_months": 3,
        "forecast_summary": _valid_summary(),
        "route_a_personal_evidence": {
            "available": True,
            "behavior_trends_summary": "stable",
            "milestone_progress_summary": "on track",
            "action_alignment_summary": "aligned",
        },
        "route_b_population_prior": {
            "available": False,
            "prior_direction": "unknown",
            "transfer_risk": "low",
            "evidence_strength": "weak",
            "population_percentile": None,
            "deviation_from_baseline": None,
            "explanation": "no data",
        },
        "calibration_divergence": {
            "divergence_status": "insufficient_data",
            "flags": [],
        },
        "outcome_targets": {
            "active_targets": 0,
            "achieved_targets": 0,
            "missed_targets": 0,
        },
        "limitations": ["test"],
        "next_evidence_to_collect": ["more data"],
    }


def test_api_create_from_forecast(client):
    resp = client.post("/forecast-snapshots/create-from-forecast", json=_forecast_result_payload())
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "saved"
    assert data["snapshot"]["locked"] is True
    assert data["snapshot"]["branch_id"] == "branch_A"
    assert "life_score" not in str(data).lower()


def test_api_list_snapshots(client):
    client.post("/forecast-snapshots/create-from-forecast", json=_forecast_result_payload())
    resp = client.get("/forecast-snapshots/list")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1


def test_api_get_snapshot(client):
    post_resp = client.post("/forecast-snapshots/create-from-forecast", json=_forecast_result_payload())
    snapshot_id = post_resp.json()["snapshot"]["snapshot_id"]
    resp = client.get(f"/forecast-snapshots/{snapshot_id}")
    assert resp.status_code == 200
    assert resp.json()["snapshot"]["snapshot_id"] == snapshot_id


def test_api_get_nonexistent_snapshot(client):
    resp = client.get("/forecast-snapshots/nonexistent_id")
    assert resp.status_code == 404


def test_snapshot_no_active_yaml_write(tmp_path: Path):
    record = ForecastSnapshotRecord(**_valid_snapshot())
    path = save_snapshot(record, repo_root=tmp_path)
    assert "alters/product/forecast_snapshots" in str(path)
    assert "alters/current" not in str(path)


def test_snapshot_no_rubric_write(tmp_path: Path):
    record = ForecastSnapshotRecord(**_valid_snapshot())
    path = save_snapshot(record, repo_root=tmp_path)
    relative = str(path.relative_to(tmp_path))
    assert "rubric" not in relative.lower()
