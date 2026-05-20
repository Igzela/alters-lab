"""Tests for P4-M5 Rubric Delta Suggestion API."""

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
    r = client.get("/rubric-delta/health")
    assert r.status_code == 200
    assert r.json()["rubric_write_allowed"] is False


def test_suggest_insufficient_data(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.rubric_delta._repo_root", lambda: tmp_path)
    r = client.post("/rubric-delta/suggest", json={"min_records": 2})
    assert r.status_code == 200
    assert r.json()["status"] == "insufficient_data"


def test_suggest_rejects_write_rubric(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.rubric_delta._repo_root", lambda: tmp_path)
    r = client.post("/rubric-delta/suggest", json={"write_rubric": True})
    assert r.status_code == 422


def test_suggest_save_uses_tmp_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.rubric_delta._repo_root", lambda: tmp_path)
    _record(tmp_path, "score_api_one", 1, 5)
    _record(tmp_path, "score_api_two", 1, 5)
    r = client.post("/rubric-delta/suggest", json={"save_suggestion": True})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "saved"
    assert data["suggestion"]["rubric_write_allowed"] is False
    assert data["suggestion_path"].startswith(str(tmp_path))


def test_list(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.rubric_delta._repo_root", lambda: tmp_path)
    r = client.get("/rubric-delta/list")
    assert r.status_code == 200
    assert r.json()["count"] == 0
