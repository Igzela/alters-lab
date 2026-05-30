"""Tests for provider-backed dialogue preview API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import alters_lab.services.provider_dialogue_preview as preview_service
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


def _mock_state(mode: str, **extra):
    defaults = {"secret_storage": "secrets_yaml_fallback", "key_name": "test-key"}
    defaults.update(extra)
    return type("S", (), {"mode": mode, **defaults})()


def test_dialogue_preview_health(monkeypatch, tmp_path: Path):
    lay = _layout(tmp_path)
    monkeypatch.setattr(preview_service, "_load_state", lambda layout=None: (lay, None, _mock_state("disabled")))
    client = TestClient(app)

    response = client.get("/provider-dialogue-preview/health")

    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "provider-dialogue-preview"
    assert data["live_generation_supported"] is True
    assert data["secrets_redacted"] is True


def test_dialogue_preview_status(monkeypatch, tmp_path: Path):
    lay = _layout(tmp_path)
    monkeypatch.setattr(preview_service, "_load_state", lambda layout=None: (lay, None, _mock_state("mock")))
    client = TestClient(app)

    response = client.get("/provider-dialogue-preview/status")

    assert response.status_code == 200
    data = response.json()
    assert data["provider_mode"] == "mock"
    assert data["configured"] is True
    assert data["persistence_supported"] is False


def test_dialogue_preview_generate_mock(monkeypatch, tmp_path: Path):
    lay = _layout(tmp_path)
    monkeypatch.setattr(preview_service, "_load_state", lambda layout=None: (lay, None, _mock_state("mock")))
    client = TestClient(app)

    response = client.post(
        "/provider-dialogue-preview/generate",
        json={"prompt": "test prompt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["provider_mode"] == "mock"
    assert data["network_call_made"] is False
    assert data["output_preview"] is not None
    assert data["output_label"] == "unverified_provider_preview"


def test_dialogue_preview_generate_disabled(monkeypatch, tmp_path: Path):
    lay = _layout(tmp_path)
    monkeypatch.setattr(preview_service, "_load_state", lambda layout=None: (lay, None, _mock_state("disabled")))
    client = TestClient(app)

    response = client.post(
        "/provider-dialogue-preview/generate",
        json={"prompt": "test prompt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"
    assert data["network_call_made"] is False


def test_dialogue_preview_generate_blocks_persist(monkeypatch, tmp_path: Path):
    lay = _layout(tmp_path)
    state = _mock_state("openai-compatible-http", base_url="http://127.0.0.1:9999/v1", model="m")
    monkeypatch.setattr(preview_service, "_load_state", lambda layout=None: (lay, None, state))
    client = TestClient(app)

    response = client.post(
        "/provider-dialogue-preview/generate",
        json={"prompt": "test prompt", "persist_output": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["output_persisted"] is False


def test_dialogue_preview_generate_no_api_key_leak(monkeypatch, tmp_path: Path):
    lay = _layout(tmp_path)
    monkeypatch.setattr(preview_service, "_load_state", lambda layout=None: (lay, None, _mock_state("mock")))
    client = TestClient(app)

    response = client.post(
        "/provider-dialogue-preview/generate",
        json={"prompt": "test prompt"},
    )

    assert response.status_code == 200
    body = response.text
    assert "sk-" not in body
    assert "api_key" not in response.json() or response.json().get("api_key") is None


def test_dialogue_preview_generate_no_yaml_writes(monkeypatch, tmp_path: Path):
    lay = _layout(tmp_path)
    monkeypatch.setattr(preview_service, "_load_state", lambda layout=None: (lay, None, _mock_state("mock")))
    client = TestClient(app)

    response = client.post(
        "/provider-dialogue-preview/generate",
        json={"prompt": "test prompt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["active_yaml_modified"] is False
    assert data["rubric_modified"] is False
    assert data["reality_score_created"] is False
    assert data["action_alignment_created"] is False
    assert data["behavior_validated"] is False
    assert data["p6_sealed"] is False
