"""Tests for provider adapter contract API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import alters_lab.services.provider_adapter as adapter_service
import alters_lab.services.provider_config as provider_config_service
from alters_lab.main import app
from alters_lab.services.runtime_layout import RuntimeLayout, resolve_runtime_layout


def _layout(tmp_path: Path) -> RuntimeLayout:
    repo = tmp_path / "repo"
    repo.mkdir()
    return resolve_runtime_layout(
        mode="dev",
        repo_root=repo,
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
    )


def _client(monkeypatch, tmp_path: Path) -> TestClient:
    layout = _layout(tmp_path)
    monkeypatch.setattr(adapter_service, "get_provider_status", lambda layout=None: _provider_status(layout))
    monkeypatch.setattr(provider_config_service, "resolve_runtime_layout", lambda: layout)
    return TestClient(app)


def _provider_status(layout=None):
    from alters_lab.services.provider_config import get_provider_status
    return get_provider_status(layout)


def test_adapter_health(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.get("/provider-adapter/health")

    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "provider-adapter"
    assert data["real_network_calls_enabled"] is False
    assert data["secrets_redacted"] is True


def test_adapter_status_exposes_safety_flags(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.get("/provider-adapter/status")

    assert response.status_code == 200
    data = response.json()
    assert data["real_network_calls_enabled"] is False
    assert data["provider_output_persists_by_default"] is False
    assert data["provider_output_can_write_active_yaml"] is False
    assert data["provider_output_can_generate_reality_score"] is False
    assert data["provider_output_can_generate_action_alignment"] is False
    assert data["behavior_validated"] is False
    assert data["p6_sealed"] is False


def test_preview_disabled_returns_skipped(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/provider-adapter/preview",
        json={"mode": "disabled", "prompt": "test prompt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"
    assert data["network_call_made"] is False
    assert data["output_persisted"] is False


def test_preview_mock_returns_deterministic(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/provider-adapter/preview",
        json={"mode": "mock", "prompt": "test prompt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["network_call_made"] is False
    assert data["output_preview"] is not None
    assert "mock" in data["output_preview"].lower()


def test_preview_blocks_live_check(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/provider-adapter/preview",
        json={"mode": "mock", "prompt": "test prompt", "live_check": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["network_call_made"] is False
    assert "P8-M2" in data["message"]


def test_preview_blocks_persist_output(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/provider-adapter/preview",
        json={"mode": "mock", "prompt": "test prompt", "persist_output": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["output_persisted"] is False


def test_preview_never_returns_api_key(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/provider-adapter/preview",
        json={"mode": "mock", "prompt": "test prompt"},
    )

    assert response.status_code == 200
    body = response.text
    assert "api_key" not in response.json() or response.json().get("api_key") is None
    assert "sk-" not in body


def test_preview_no_active_yaml_rubric_writes(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/provider-adapter/preview",
        json={"mode": "mock", "prompt": "test prompt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["active_yaml_modified"] is False
    assert data["rubric_modified"] is False
    assert data["reality_score_created"] is False
    assert data["action_alignment_created"] is False
    assert data["behavior_validated"] is False
    assert data["p6_sealed"] is False


def test_existing_provider_config_tests_still_pass(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    health = client.get("/provider-config/health")
    assert health.status_code == 200
    assert health.json()["component"] == "provider-config"

    status = client.get("/provider-config/status")
    assert status.status_code == 200
    assert status.json()["provider_mode"] == "disabled"
