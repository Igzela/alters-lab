"""Tests for P4-M7 Checkpoint Regeneration Plan API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app
from alters_lab.schemas.calibration_loop import RealityScoreRequest
from alters_lab.services.calibration_loop import submit_reality_score

client = TestClient(app)


def _scores(value: int) -> dict:
    return {
        "execution_discipline": value,
        "exploration_freedom": value,
        "life_state_match": value,
        "energy_level": value,
    }


def _record(tmp_path, score_id: str, actual: int, expected: int):
    submit_reality_score(RealityScoreRequest(
        score_id=score_id,
        branch_id="branch_A",
        alter_id="alter_A",
        actual_scores=_scores(actual),
        expected_scores=_scores(expected),
        submitted_by_user=True,
    ), tmp_path)


def test_health():
    r = client.get("/checkpoint-regeneration/health")
    assert r.status_code == 200
    assert r.json()["regeneration_allowed_now"] is False


def test_plan_no_action(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.checkpoint_regeneration._repo_root", lambda: tmp_path)
    r = client.post("/checkpoint-regeneration/plan", json={"drift_threshold": 0.6})
    assert r.status_code == 200
    assert r.json()["status"] == "no_action"


def test_plan_high_drift(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.checkpoint_regeneration._repo_root", lambda: tmp_path)
    _record(tmp_path, "score_api_high", 1, 5)
    r = client.post("/checkpoint-regeneration/plan", json={"drift_threshold": 0.6})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "plan_created"
    assert data["plan"]["active_write_allowed"] is False
    assert data["plan"]["regeneration_allowed_now"] is False


def test_plan_rejects_regenerate(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.checkpoint_regeneration._repo_root", lambda: tmp_path)
    r = client.post("/checkpoint-regeneration/plan", json={"regenerate": True})
    assert r.status_code == 422


def test_list(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.checkpoint_regeneration._repo_root", lambda: tmp_path)
    r = client.get("/checkpoint-regeneration/list")
    assert r.status_code == 200
    assert r.json()["count"] == 0
