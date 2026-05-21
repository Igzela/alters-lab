"""API tests for P7 runtime layout routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_runtime_layout_route_inventory():
    routes = sorted(route.path for route in app.routes)
    expected = [
        "/runtime-layout/health",
        "/runtime-layout/status",
        "/runtime-layout/ensure-config",
    ]
    for route in expected:
        assert route in routes


def test_runtime_layout_health():
    response = client.get("/runtime-layout/health")

    assert response.status_code == 200
    assert response.json()["component"] == "runtime-layout"
    assert response.json()["default_safe"] is True


def test_runtime_layout_status_redacts_secrets_and_does_not_create_config(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("ALTERS_LAB_MODE", "packaged")

    response = client.get("/runtime-layout/status")

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "packaged"
    assert data["config_path"] == str(home / ".config" / "alters-lab" / "config.yaml")
    assert data["data_dir"] == str(home / ".local" / "share" / "alters-lab")
    assert data["product_data_dir"] == str(home / ".local" / "share" / "alters-lab" / "product")
    assert data["logs_dir"] == str(home / ".local" / "state" / "alters-lab" / "logs")
    assert data["provider_mode"] == "disabled"
    assert data["secrets_storage"] == "keyring"
    assert data["secrets_redacted"] is True
    assert data["active_yaml_write_allowed"] is False
    assert data["rubric_write_allowed"] is False
    assert not (home / ".config" / "alters-lab" / "config.yaml").exists()


def test_runtime_layout_ensure_config_creates_config_only(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("ALTERS_LAB_MODE", "packaged")

    response = client.post("/runtime-layout/ensure-config")

    assert response.status_code == 200
    data = response.json()
    assert data["config_path"] == str(home / ".config" / "alters-lab" / "config.yaml")
    assert data["secrets_written"] is False
    assert data["runtime_records_written"] is False
    assert data["active_yaml_modified"] is False
    assert data["rubric_modified"] is False
    assert (home / ".config" / "alters-lab" / "config.yaml").exists()
    assert not (home / ".config" / "alters-lab" / "secrets.yaml").exists()
    assert not (home / ".local" / "share" / "alters-lab" / "product").exists()


def test_runtime_layout_safety_flags_false_in_dev(tmp_path, monkeypatch):
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/runtime-layout/status")

    assert response.status_code == 200
    assert response.json()["mode"] == "dev"
    assert response.json()["active_yaml_write_allowed"] is False
    assert response.json()["rubric_write_allowed"] is False

