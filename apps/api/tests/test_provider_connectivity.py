"""Tests for provider connectivity check service."""

from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.provider_connectivity import (
    ProviderConnectivityAuditEvent,
    ProviderConnectivityHealthResponse,
    ProviderConnectivityRequest,
    ProviderConnectivityResponse,
    ProviderConnectivityStatusResponse,
)
from alters_lab.services.provider_connectivity import (
    LIVE_CONFIRMATION,
    build_provider_connectivity_audit_event,
    build_provider_connectivity_status,
    run_provider_connectivity_check,
)
from alters_lab.services.provider_config import (
    ProviderConfigUpdateRequest,
    store_provider_secret,
    update_provider_config,
)
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


def _configured_layout(tmp_path: Path) -> RuntimeLayout:
    layout = _layout(tmp_path)
    update_provider_config(
        ProviderConfigUpdateRequest(
            mode="openai-compatible-http",
            base_url="http://127.0.0.1:9999/v1",
            model="test-model",
            secret_storage="secrets_yaml_fallback",
            explicit_user_configuration=True,
        ),
        layout,
    )
    store_provider_secret("test-key-not-real", "secrets_yaml_fallback", "store-secret", layout)
    return layout


def _fake_http_200(url: str, headers: dict, timeout: int) -> tuple[int, bytes]:
    return 200, b'{"data": []}'


def _fake_http_401(url: str, headers: dict, timeout: int) -> tuple[int, bytes]:
    return 401, b'{"error": "unauthorized"}'


def _fake_http_500(url: str, headers: dict, timeout: int) -> tuple[int, bytes]:
    return 500, b'{"error": "internal"}'


def _fake_http_timeout(url: str, headers: dict, timeout: int) -> tuple[int, bytes]:
    raise TimeoutError("connection timed out")


# --- Service tests ---


def test_disabled_returns_skipped_no_network(tmp_path: Path):
    req = ProviderConnectivityRequest()
    resp = run_provider_connectivity_check(req, _layout(tmp_path))

    assert resp.status == "skipped"
    assert resp.network_call_made is False
    assert resp.provider_mode == "disabled"


def test_mock_returns_ok_no_network(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(ProviderConfigUpdateRequest(mode="mock"), layout)
    req = ProviderConnectivityRequest()
    resp = run_provider_connectivity_check(req, layout)

    assert resp.status == "ok"
    assert resp.network_call_made is False
    assert resp.provider_reachable is True
    assert resp.auth_valid is True


def test_openai_unconfigured_returns_blocked_no_network(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    # Delete the secret so it's unconfigured
    from alters_lab.services.provider_config import delete_provider_secret
    delete_provider_secret("delete-secret", "secrets_yaml_fallback", layout)

    req = ProviderConnectivityRequest(live_check=True, confirmation=LIVE_CONFIRMATION)
    resp = run_provider_connectivity_check(req, layout)

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert resp.configured is False


def test_dry_run_returns_no_network(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest(dry_run=True)
    resp = run_provider_connectivity_check(req, layout)

    assert resp.status == "ok"
    assert resp.network_call_made is False


def test_dry_run_false_live_check_false_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest(dry_run=False, live_check=False)
    resp = run_provider_connectivity_check(req, layout)

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "live_check=true" in resp.message.lower()


def test_live_check_without_confirmation_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest(live_check=True)
    resp = run_provider_connectivity_check(req, layout)

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "confirmation" in resp.message.lower()


def test_live_check_wrong_confirmation_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest(live_check=True, confirmation="wrong-phrase")
    resp = run_provider_connectivity_check(req, layout)

    assert resp.status == "blocked"
    assert resp.network_call_made is False


def test_live_check_exact_confirmation_uses_injected_client(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest(
        live_check=True, confirmation=LIVE_CONFIRMATION, dry_run=False,
    )
    resp = run_provider_connectivity_check(req, layout, http_client=_fake_http_200)

    assert resp.network_call_made is True
    assert resp.provider_reachable is True
    assert resp.auth_valid is True
    assert resp.status_code == 200


def test_2xx_maps_reachable_true_auth_valid_true(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest(
        live_check=True, confirmation=LIVE_CONFIRMATION, dry_run=False,
    )
    resp = run_provider_connectivity_check(req, layout, http_client=_fake_http_200)

    assert resp.provider_reachable is True
    assert resp.auth_valid is True
    assert resp.status == "ok"


def test_401_maps_reachable_true_auth_valid_false(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest(
        live_check=True, confirmation=LIVE_CONFIRMATION, dry_run=False,
    )
    resp = run_provider_connectivity_check(req, layout, http_client=_fake_http_401)

    assert resp.provider_reachable is True
    assert resp.auth_valid is False
    assert resp.status == "error"
    assert resp.error_type == "auth_failed"


def test_timeout_maps_reachable_false(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest(
        live_check=True, confirmation=LIVE_CONFIRMATION, dry_run=False,
    )
    resp = run_provider_connectivity_check(req, layout, http_client=_fake_http_timeout)

    assert resp.provider_reachable is False
    assert resp.auth_valid is None
    assert resp.status == "error"


def test_response_never_includes_api_key(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest()
    resp = run_provider_connectivity_check(req, layout)
    dumped = resp.model_dump()

    assert "api_key" not in dumped
    assert "sk-" not in str(dumped)


def test_audit_event_contains_no_prompt_response_secret():
    event = build_provider_connectivity_audit_event(
        provider_mode="mock", status="ok", live_check=False,
        dry_run=True, network_call_made=False,
    )
    dumped = event.model_dump()
    assert "prompt" not in dumped or dumped.get("prompt") is None
    assert "response" not in dumped or dumped.get("response") is None
    assert "api_key" not in dumped
    assert event.prompt_recorded is False
    assert event.response_recorded is False
    assert event.secret_recorded is False
    assert event.redacted is True


def test_no_active_yaml_rubric_writes(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest()
    resp = run_provider_connectivity_check(req, layout)

    assert resp.active_yaml_modified is False
    assert resp.rubric_modified is False
    assert resp.reality_score_created is False
    assert resp.action_alignment_created is False


def test_p6_false_flags_remain_false(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest()
    resp = run_provider_connectivity_check(req, layout)

    assert resp.p6_behavior_validated is False
    assert resp.p6_sealed is False


def test_prompt_content_sent_literal_false(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest()
    resp = run_provider_connectivity_check(req, layout)
    assert resp.prompt_content_sent is False


def test_response_content_persisted_literal_false(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    req = ProviderConnectivityRequest()
    resp = run_provider_connectivity_check(req, layout)
    assert resp.response_content_persisted is False


# --- Contract hardening: invalid constructions ---


def test_response_rejects_prompt_content_sent_true():
    with pytest.raises(Exception):
        ProviderConnectivityResponse(
            status="ok", provider_mode="mock", configured=True,
            live_check=False, dry_run=True, network_call_made=False,
            message="test", prompt_content_sent=True,
        )


def test_response_rejects_response_content_persisted_true():
    with pytest.raises(Exception):
        ProviderConnectivityResponse(
            status="ok", provider_mode="mock", configured=True,
            live_check=False, dry_run=True, network_call_made=False,
            message="test", response_content_persisted=True,
        )


def test_response_rejects_secrets_redacted_false():
    with pytest.raises(Exception):
        ProviderConnectivityResponse(
            status="ok", provider_mode="mock", configured=True,
            live_check=False, dry_run=True, network_call_made=False,
            message="test", secrets_redacted=False,
        )


def test_health_rejects_live_network_supported_false():
    with pytest.raises(Exception):
        ProviderConnectivityHealthResponse(live_network_supported=False)


def test_status_rejects_live_network_requires_confirmation_false():
    with pytest.raises(Exception):
        ProviderConnectivityStatusResponse(
            provider_mode="mock", configured=True, key_configured=False,
            live_network_requires_confirmation=False,
        )


def test_status_rejects_dry_run_default_false():
    with pytest.raises(Exception):
        ProviderConnectivityStatusResponse(
            provider_mode="mock", configured=True, key_configured=False,
            dry_run_default=False,
        )
