"""Tests for P5-M5 Durable Storage Boundary API routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    r = client.get("/storage-boundary/health")
    assert r.status_code == 200
    data = r.json()
    assert data["component"] == "storage-boundary"
    assert data["default_backend"] == "yaml"
    assert data["database_added"] is False


def test_manifest():
    r = client.get("/storage-boundary/manifest")
    assert r.status_code == 200
    data = r.json()
    assert data["default_backend"] == "yaml"
    assert data["database_implemented"] is False
    assert data["no_migration"] is True
    assert isinstance(data["active_yaml_read_only"], list)
    assert isinstance(data["calibration_score_write"], list)
    assert isinstance(data["product_session_write"], list)


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/storage-boundary/health" in routes
    assert "/storage-boundary/manifest" in routes
