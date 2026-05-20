"""Tests for P4 calibration loop API."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def _scores(value: int = 3) -> dict:
    return {
        "execution_discipline": value,
        "exploration_freedom": value,
        "life_state_match": value,
        "energy_level": value,
    }


def _payload(**overrides) -> dict:
    data = {
        "score_id": "score_api_001",
        "branch_id": "branch_A",
        "alter_id": "alter_A",
        "actual_scores": _scores(3),
        "user_notes": "Explicit API score.",
        "evidence_refs": ["manual-note"],
    }
    data.update(overrides)
    return data


def test_health():
    r = client.get("/calibration-loop/health")
    assert r.status_code == 200
    data = r.json()
    assert data["component"] == "calibration-loop"
    assert data["provider_used"] is False
    assert data["active_write_allowed"] is False
    assert data["rubric_write_allowed"] is False


def test_submit_reality_score(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    r = client.post("/calibration-loop/reality-scores", json=_payload())
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "recorded"
    assert data["record"]["id"] == "score_api_001"
    assert data["record"]["drift"] is None
    assert data["record"]["submitted_by_user"] is True
    assert data["boundary_confirmations"]["active_yaml_modified"] is False
    assert Path(data["score_path"]).exists()
    assert not (tmp_path / "alters" / "current").exists()


def test_submit_reality_score_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    first = client.post("/calibration-loop/reality-scores", json=_payload())
    second = client.post("/calibration-loop/reality-scores", json=_payload())
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["status"] == "already_exists"


def test_submit_reality_score_rejects_extra_provider(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    r = client.post("/calibration-loop/reality-scores", json=_payload(provider="openai"))
    assert r.status_code == 422


def test_submit_reality_score_rejects_non_user_submission(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    r = client.post("/calibration-loop/reality-scores", json=_payload(submitted_by_user=False))
    assert r.status_code == 422


def test_submit_reality_score_rejects_invalid_dimension(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    r = client.post(
        "/calibration-loop/reality-scores",
        json=_payload(actual_scores={**_scores(3), "energy_level": 9}),
    )
    assert r.status_code == 422


def test_submit_reality_score_rejects_branch_alter_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    r = client.post("/calibration-loop/reality-scores", json=_payload(branch_id="branch_B"))
    assert r.status_code == 422


def test_drift_calculate_is_response_only(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    r = client.post(
        "/calibration-loop/drift/calculate",
        json={
            "score_id": "score_api_001",
            "branch_id": "branch_A",
            "alter_id": "alter_A",
            "expected_scores": _scores(5),
            "actual_scores": _scores(1),
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["overall"] == 1.0
    assert data["threshold_exceeded"] is True
    assert data["evidence_only"] is True
    assert data["regeneration_triggered"] is False
    assert data["rubric_modified"] is False
    assert not (tmp_path / "alters").exists()


def test_history_empty(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    r = client.get("/calibration-loop/history")
    assert r.status_code == 200
    data = r.json()
    assert data["read_only"] is True
    assert data["count"] == 0
    assert data["records"] == []
    assert data["drift_evidence"] == []


def test_history_reads_existing_score_without_writing(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.calibration_loop._repo_root", lambda: tmp_path)
    scores_dir = tmp_path / "alters" / "calibration" / "scores"
    scores_dir.mkdir(parents=True)
    score_path = scores_dir / "score_history_001.yaml"
    score_path.write_text(yaml.safe_dump({
        "id": "score_history_001",
        "status": "recorded",
        "created_at": "2026-05-20T00:00:00+00:00",
        "branch_id": "branch_A",
        "alter_id": "alter_A",
        "input_refs": {
            "snapshot_ref": "alters/current/snapshot.yaml",
            "branches_ref": "alters/current/branches.yaml",
            "alter_ref": "alters/current/alters/alter_A.yaml",
            "rubric_ref": "alters/calibration/rubric.yaml",
        },
        "actual_scores": _scores(3),
        "expected_scores": _scores(5),
        "drift": None,
        "user_notes": "Existing explicit score.",
        "evidence_refs": [],
        "submitted_by_user": True,
        "source": "explicit_user_submission",
        "caller": "api",
        "boundary_confirmations": {
            "active_yaml_modified": False,
            "rubric_modified": False,
            "provider_used": False,
            "frontend_added": False,
            "database_added": False,
            "archive_created": False,
            "regeneration_triggered": False,
            "promotion_triggered": False,
            "reality_score_requires_explicit_user_submission": True,
            "drift_evidence_only": True,
            "calibration_history_read_only": True,
        },
    }), encoding="utf-8")
    before = score_path.read_text(encoding="utf-8")
    r = client.get("/calibration-loop/history")
    after = score_path.read_text(encoding="utf-8")
    assert r.status_code == 200
    data = r.json()
    assert before == after
    assert data["count"] == 1
    assert data["records"][0]["id"] == "score_history_001"
    assert data["drift_evidence"][0]["overall"] == 0.5


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/calibration-loop/health" in routes
    assert "/calibration-loop/reality-scores" in routes
    assert "/calibration-loop/drift/calculate" in routes
    assert "/calibration-loop/history" in routes


def test_no_provider_imports():
    import alters_lab.api.calibration_loop as api_mod
    import alters_lab.services.calibration_loop as svc_mod

    for path in [api_mod.__file__, svc_mod.__file__]:
        content = Path(path).read_text(encoding="utf-8").lower()
        for pattern in ["openai", "anthropic", "openrouter", "litellm", "langchain", "crewai"]:
            assert pattern not in content
