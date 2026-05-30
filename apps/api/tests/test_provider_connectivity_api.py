"""Tests for provider connectivity check API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import alters_lab.services.provider_connectivity as connectivity_service
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
    monkeypatch.setattr(provider_config_service, "resolve_runtime_layout", lambda: layout)
    return TestClient(app)


def test_connectivity_health(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.get("/provider-connectivity/health")

    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "provider-connectivity"
    assert data["live_network_supported"] is True
    assert data["live_network_requires_confirmation"] is True
    assert data["secrets_redacted"] is True


def test_connectivity_status_exposes_safety_flags(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.get("/provider-connectivity/status")

    assert response.status_code == 200
    data = response.json()
    assert data["dry_run_default"] is True
    assert data["live_network_requires_confirmation"] is True
    assert data["provider_output_persists_by_default"] is False
    assert data["behavior_validated"] is False
    assert data["p6_sealed"] is False


def test_check_disabled_returns_skipped(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post("/provider-connectivity/check", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"
    assert data["network_call_made"] is False


def test_check_mock_returns_ok(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    client.post("/provider-config/config", json={"mode": "mock"})

    response = client.post("/provider-connectivity/check", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["provider_reachable"] is True


def test_check_live_without_confirmation_blocks(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    client.post(
        "/provider-config/config",
        json={
            "mode": "openai-compatible-http",
            "base_url": "http://127.0.0.1:9999/v1",
            "model": "test-model",
            "secret_storage": "secrets_yaml_fallback",
            "explicit_user_configuration": True,
        },
    )
    client.post(
        "/provider-config/secret",
        json={
            "api_key": "test-key-not-real",
            "storage": "secrets_yaml_fallback",
            "confirmation": "store-secret",
        },
    )

    response = client.post(
        "/provider-connectivity/check",
        json={"live_check": True, "dry_run": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["network_call_made"] is False


def test_check_never_returns_api_key(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post("/provider-connectivity/check", json={})

    assert response.status_code == 200
    assert "api_key" not in response.json()
    assert "sk-" not in response.text


def test_adapter_preview_still_no_network(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/provider-adapter/preview",
        json={"mode": "mock", "prompt": "test"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["network_call_made"] is False
    assert data["output_persisted"] is False


def test_existing_provider_config_tests_still_pass(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    health = client.get("/provider-config/health")
    assert health.status_code == 200
    assert health.json()["component"] == "provider-config"

    status = client.get("/provider-config/status")
    assert status.status_code == 200
    assert status.json()["provider_mode"] == "disabled"
