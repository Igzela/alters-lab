"""Tests for P5-M2 Provider Gateway service."""

from __future__ import annotations

import os

import pytest

from alters_lab.schemas.provider_gateway import (
    ProviderGatewayRequest,
    ProviderGatewayResponse,
)
from alters_lab.services.provider_gateway import (
    _get_provider_mode,
    _get_provider_api_key,
    _redact_secrets,
    get_provider_gateway_health,
    get_provider_config_status,
    provider_gateway_complete,
)


def test_default_mode_is_mock(monkeypatch):
    monkeypatch.delenv("ALTERS_PROVIDER_MODE", raising=False)
    monkeypatch.setattr("alters_lab.services.provider_gateway._resolve_config_value", lambda f: None)
    assert _get_provider_mode() == "mock"


def test_mock_gateway_works():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        req = ProviderGatewayRequest(messages=[{"role": "user", "content": "Hello"}])
        resp = provider_gateway_complete(req)
        assert isinstance(resp, ProviderGatewayResponse)
        assert resp.status == "mock_response"
        assert resp.persisted is False
        assert resp.active_yaml_modified is False
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_disabled_mode_rejects():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "disabled"
        req = ProviderGatewayRequest(messages=[{"role": "user", "content": "Hello"}])
        resp = provider_gateway_complete(req)
        assert resp.status == "disabled"
        assert resp.persisted is False
        assert resp.active_yaml_modified is False
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_env_api_key_not_returned():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-secret-key-12345"
        resp = get_provider_config_status()
        # Gateway never returns actual key material
        assert resp.api_key_configured is True
        assert "sk-test" not in str(resp.model_dump())
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original
        os.environ.pop("ALTERS_PROVIDER_API_KEY", None)


def test_no_provider_sdk_imports():
    import alters_lab.services.provider_gateway as mod
    content = open(mod.__file__).read().lower()
    for pattern in ["from openai", "import openai", "from anthropic", "import anthropic"]:
        assert pattern not in content


def test_response_persisted_false():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        req = ProviderGatewayRequest(messages=[{"role": "user", "content": "test"}])
        resp = provider_gateway_complete(req)
        assert resp.persisted is False
        assert resp.active_yaml_modified is False
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_no_secrets_in_response():
    original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
    original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-secret-key-12345"
        req = ProviderGatewayRequest(messages=[{"role": "user", "content": "test"}])
        resp = provider_gateway_complete(req)
        assert "sk-" not in resp.content
        assert "sk-test" not in resp.content
        assert resp.redaction_summary.get("api_key_exposed") is False
    finally:
        if original_mode is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original_mode
        else:
            os.environ.pop("ALTERS_PROVIDER_MODE", None)
        if original_key is not None:
            os.environ["ALTERS_PROVIDER_API_KEY"] = original_key
        else:
            os.environ.pop("ALTERS_PROVIDER_API_KEY", None)


def test_health_response():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        r = get_provider_gateway_health()
        assert r.status == "ok"
        assert r.component == "provider-gateway"
        assert r.mode == "mock"
        assert r.no_secrets_exposed is True
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_redact_secrets():
    text = "Here is my key: sk-abc123def456ghi789jkl012mno345 and Bearer token123.abc.def"
    redacted = _redact_secrets(text)
    assert "sk-abc123" not in redacted
    assert "[REDACTED]" in redacted
