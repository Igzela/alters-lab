"""Tests for weekly review assistant API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import alters_lab.services.weekly_review_assistant as wr_service
from alters_lab.main import app
from alters_lab.services.provider_config import (
    ProviderConfigUpdateRequest,
    store_provider_secret,
    update_provider_config,
)
from alters_lab.services.runtime_layout import resolve_runtime_layout


def _layout(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    return resolve_runtime_layout(
        mode="dev",
        repo_root=repo,
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
    )


client = TestClient(app)


def test_health_route():
    resp = client.get("/weekly-review-assistant/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["component"] == "weekly-review-assistant"
    assert data["output_persisted_by_default"] is False
    assert data["secrets_redacted"] is True


def test_status_route():
    resp = client.get("/weekly-review-assistant/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "provider_mode" in data
    assert data["behavior_validated"] is False
    assert data["p6_sealed"] is False
    assert data["suggestion_persistence_supported"] is False


def test_suggest_dry_run_default(monkeypatch, tmp_path: Path):
    lay = _layout(tmp_path)
    mock_state = type("S", (), {"mode": "disabled", "secret_storage": "secrets_yaml_fallback", "key_name": "test-key"})()
    monkeypatch.setattr(wr_service, "_load_state", lambda layout=None: (lay, None, mock_state))
    c = TestClient(app)
    resp = c.post("/weekly-review-assistant/suggest", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "skipped"  # disabled by default
    assert data["network_call_made"] is False


def test_suggest_blocks_persist():
    resp = client.post("/weekly-review-assistant/suggest", json={"save_suggestion": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "blocked"
    assert "save_suggestion" in data["message"].lower()


def test_suggest_never_completes_review():
    resp = client.post("/weekly-review-assistant/suggest", json={})
    data = resp.json()
    assert data["weekly_review_completed"] is False


def test_suggest_never_creates_scores():
    resp = client.post("/weekly-review-assistant/suggest", json={})
    data = resp.json()
    assert data["action_alignment_created"] is False
    assert data["reality_score_created"] is False


def test_suggest_no_api_key_leak():
    resp = client.post("/weekly-review-assistant/suggest", json={})
    data = resp.json()
    dumped = str(data)
    assert "sk-" not in dumped
    assert "api_key" not in data


def test_routes_exist():
    from alters_lab.main import app as real_app

    routes = sorted(route.path for route in real_app.routes)
    assert "/weekly-review-assistant/health" in routes
    assert "/weekly-review-assistant/status" in routes
    assert "/weekly-review-assistant/suggest" in routes
