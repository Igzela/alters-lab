"""API tests for P7 unified local app server."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_local_app_route_inventory():
    routes = sorted(route.path for route in app.routes)
    expected = [
        "/local-app/health",
        "/local-app/status",
        "/local-app/frontend-status",
        "/runtime-layout/status",
    ]
    for route in expected:
        assert route in routes


def test_local_app_health_returns_backend_ready():
    response = client.get("/local-app/health")

    assert response.status_code == 200
    assert response.json()["backend_ready"] is True


def test_local_app_status_returns_safe_flags(tmp_path, monkeypatch):
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/local-app/status")

    assert response.status_code == 200
    data = response.json()
    assert data["backend_ready"] is True
    assert data["runtime_mode"] == "dev"
    assert data["api_routes_available"] is True
    assert data["provider_mode"] == "disabled"
    assert data["secrets_redacted"] is True
    assert data["behavior_validated"] is False
    assert data["p6_sealed"] is False
    assert data["active_yaml_write_allowed"] is False
    assert data["rubric_write_allowed"] is False


def test_frontend_status_false_when_dist_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/local-app/frontend-status")

    assert response.status_code == 200
    assert response.json()["frontend_available"] is False
    assert response.json()["frontend_dist_path"] == str(tmp_path / "apps" / "web" / "dist")


def test_runtime_layout_status_still_works(tmp_path, monkeypatch):
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/runtime-layout/status")

    assert response.status_code == 200
    assert response.json()["mode"] == "dev"


def test_missing_dist_root_returns_placeholder_not_crash(tmp_path, monkeypatch):
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/")

    assert response.status_code == 503
    assert "Frontend build not found" in response.text


def test_static_root_serves_index_when_dist_exists(tmp_path, monkeypatch):
    _create_fake_dist(tmp_path)
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "Fake Alters Lab" in response.text


def test_static_asset_served_when_dist_exists(tmp_path, monkeypatch):
    _create_fake_dist(tmp_path)
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/assets/app.js")

    assert response.status_code == 200
    assert "console.log('fake')" in response.text


def test_spa_fallback_serves_index_for_frontend_route(tmp_path, monkeypatch):
    _create_fake_dist(tmp_path)
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/settings/provider")

    assert response.status_code == 200
    assert "Fake Alters Lab" in response.text


def test_spa_fallback_does_not_intercept_api_routes(tmp_path, monkeypatch):
    _create_fake_dist(tmp_path)
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    runtime = client.get("/runtime-layout/status")
    local = client.get("/local-app/status")

    assert runtime.status_code == 200
    assert runtime.headers["content-type"].startswith("application/json")
    assert local.status_code == 200
    assert local.headers["content-type"].startswith("application/json")


def test_unknown_api_prefixed_route_not_spa_fallback(tmp_path, monkeypatch):
    _create_fake_dist(tmp_path)
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    response = client.get("/runtime-layout/missing")

    assert response.status_code == 404
    assert "Fake Alters Lab" not in response.text


def _create_fake_dist(repo_root):
    dist = repo_root / "apps" / "web" / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><h1>Fake Alters Lab</h1>", encoding="utf-8")
    (assets / "app.js").write_text("console.log('fake')", encoding="utf-8")
