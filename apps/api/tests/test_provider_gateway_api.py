"""Tests for P5-M2 Provider Gateway API routes."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        r = client.get("/provider-gateway/health")
        assert r.status_code == 200
        data = r.json()
        assert data["component"] == "provider-gateway"
        assert data["mode"] == "mock"
        assert data["no_secrets_exposed"] is True
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_complete_mock():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        r = client.post("/provider-gateway/complete", json={
            "messages": [{"role": "user", "content": "Hello"}],
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "mock_response"
        assert data["persisted"] is False
        assert data["active_yaml_modified"] is False
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_complete_disabled():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "disabled"
        r = client.post("/provider-gateway/complete", json={
            "messages": [{"role": "user", "content": "Hello"}],
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "disabled"
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_config_status_no_secrets():
    original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
    original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-secret"
        r = client.get("/provider-gateway/config-status")
        assert r.status_code == 200
        data = r.json()
        assert data["api_key_value"] == "[redacted]"
        assert data["no_secrets_exposed"] is True
    finally:
        if original_mode is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original_mode
        else:
            os.environ.pop("ALTERS_PROVIDER_MODE", None)
        if original_key is not None:
            os.environ["ALTERS_PROVIDER_API_KEY"] = original_key
        else:
            os.environ.pop("ALTERS_PROVIDER_API_KEY", None)


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/provider-gateway/health" in routes
    assert "/provider-gateway/complete" in routes
    assert "/provider-gateway/config-status" in routes
