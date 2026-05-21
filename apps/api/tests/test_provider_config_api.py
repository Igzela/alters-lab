"""Tests for local provider configuration API."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

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


def test_provider_config_health(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.get("/provider-config/health")

    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "provider-config"
    assert data["real_provider_default_enabled"] is False
    assert data["secrets_redacted"] is True


def test_status_redacts_secrets(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    client.post(
        "/provider-config/secret",
        json={
            "api_key": "test-key-not-real",
            "storage": "secrets_yaml_fallback",
            "confirmation": "store-secret",
        },
    )

    response = client.get("/provider-config/status")

    assert response.status_code == 200
    body = response.text
    assert "test-key-not-real" not in body
    data = response.json()
    assert data["api_key_configured"] is True
    assert data["secrets_redacted"] is True


def test_get_config_never_returns_api_key(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    client.post(
        "/provider-config/secret",
        json={
            "api_key": "test-key-not-real",
            "storage": "secrets_yaml_fallback",
            "confirmation": "store-secret",
        },
    )

    response = client.get("/provider-config/config")

    assert response.status_code == 200
    assert "test-key-not-real" not in response.text
    assert "api_key" not in response.json()


def test_post_config_writes_config_only(monkeypatch, tmp_path: Path):
    layout = _layout(tmp_path)
    monkeypatch.setattr(provider_config_service, "resolve_runtime_layout", lambda: layout)
    client = TestClient(app)

    response = client.post(
        "/provider-config/config",
        json={"mode": "mock", "model": "mock-model", "secret_storage": "secrets_yaml_fallback"},
    )

    assert response.status_code == 200
    assert layout.config_path.exists()
    assert not layout.secrets_path.exists()


def test_openai_compatible_requires_explicit_user_configuration(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/provider-config/config",
        json={
            "mode": "openai-compatible-http",
            "base_url": "http://127.0.0.1:9999/v1",
            "model": "test-model",
        },
    )

    assert response.status_code == 400
    assert "explicit_user_configuration" in response.text


def test_openai_status_requires_base_url_model_and_secret(monkeypatch, tmp_path: Path):
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

    assert client.get("/provider-config/status").json()["configured"] is False
    client.post(
        "/provider-config/secret",
        json={
            "api_key": "test-key-not-real",
            "storage": "secrets_yaml_fallback",
            "confirmation": "store-secret",
        },
    )
    status = client.get("/provider-config/status").json()
    assert status["configured"] is True
    assert status["api_key_configured"] is True


def test_secret_store_and_delete(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    stored = client.post(
        "/provider-config/secret",
        json={
            "api_key": "test-key-not-real",
            "storage": "secrets_yaml_fallback",
            "confirmation": "store-secret",
        },
    )
    deleted = client.request(
        "DELETE",
        "/provider-config/secret",
        json={"storage": "secrets_yaml_fallback", "confirmation": "delete-secret"},
    )

    assert stored.status_code == 200
    assert "test-key-not-real" not in stored.text
    assert stored.json()["api_key_configured"] is True
    assert deleted.status_code == 200
    assert deleted.json()["api_key_configured"] is False


def test_provider_config_test_modes_do_not_call_network(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    disabled = client.post("/provider-config/test", json={}).json()
    assert disabled["status"] == "skipped"
    assert disabled["network_call_made"] is False

    client.post("/provider-config/config", json={"mode": "mock"})
    mock = client.post("/provider-config/test", json={}).json()
    assert mock["status"] == "ok"
    assert mock["network_call_made"] is False


def test_provider_config_test_openai_dry_run(monkeypatch, tmp_path: Path):
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

    response = client.post("/provider-config/test", json={"dry_run": True})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "misconfigured"
    assert data["network_call_made"] is False
    assert data["p6_behavior_validated"] is False
    assert data["p6_sealed"] is False
