"""Tests for P5-M1 API Product Surface API routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    r = client.get("/product/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["component"] == "product-surface"
    assert data["read_only"] is True


def test_routes():
    r = client.get("/product/routes")
    assert r.status_code == 200
    data = r.json()
    assert "safe_routes" in data
    assert "internal_routes" in data
    assert "dangerous_routes" in data
    assert data["total"] > 0


def test_status():
    r = client.get("/product/status")
    assert r.status_code == 200
    data = r.json()
    assert data["phase3_status"] == "sealed_with_notes"
    assert data["phase4_status"] == "pass"
    assert data["provider_gateway_status"] == "mock_default"
    assert data["storage_backend"] == "yaml"
    assert data["no_secrets_exposed"] is True
    assert isinstance(data["safe_public_endpoints"], list)
    assert isinstance(data["internal_only_endpoints"], list)


def test_workflow_capabilities():
    r = client.get("/product/workflow-capabilities")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["read_only"] is True
    assert len(data["capabilities"]) > 0


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/product/health" in routes
    assert "/product/routes" in routes
    assert "/product/status" in routes
    assert "/product/workflow-capabilities" in routes
