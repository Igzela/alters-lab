"""Tests for provider adapter contract service."""

from __future__ import annotations

from pathlib import Path

import yaml

from alters_lab.schemas.provider_adapter import (
    ProviderAdapterRequest,
    ProviderAdapterResponse,
    ProviderAuditEvent,
)
from alters_lab.services.provider_adapter import (
    build_provider_adapter_health,
    build_provider_adapter_status,
    build_provider_audit_event,
    redact_provider_error,
    run_provider_adapter,
    validate_provider_request,
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


def test_disabled_mode_returns_skipped_no_network(tmp_path: Path):
    request = ProviderAdapterRequest(mode="disabled", prompt="test")
    response = run_provider_adapter(request, _layout(tmp_path))

    assert response.status == "skipped"
    assert response.network_call_made is False
    assert response.output_preview is None
    assert response.output_persisted is False


def test_mock_mode_returns_deterministic_preview_no_network(tmp_path: Path):
    request = ProviderAdapterRequest(mode="mock", prompt="test")
    response = run_provider_adapter(request, _layout(tmp_path))

    assert response.status == "ok"
    assert response.network_call_made is False
    assert response.output_preview is not None
    assert "mock" in response.output_preview.lower()
    assert response.output_persisted is False


def test_openai_compatible_http_dry_run_no_network(tmp_path: Path):
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

    request = ProviderAdapterRequest(mode="openai-compatible-http", prompt="test")
    response = run_provider_adapter(request, layout)

    assert response.network_call_made is False
    assert response.status in ("ok", "blocked")


def test_live_check_true_is_blocked_no_network(tmp_path: Path):
    request = ProviderAdapterRequest(mode="mock", prompt="test", live_check=True)
    response = run_provider_adapter(request, _layout(tmp_path))

    assert response.status == "blocked"
    assert response.network_call_made is False
    assert "live_check" in response.message.lower() or "P8-M2" in response.message


def test_persist_output_true_is_blocked(tmp_path: Path):
    request = ProviderAdapterRequest(mode="mock", prompt="test", persist_output=True)
    response = run_provider_adapter(request, _layout(tmp_path))

    assert response.status == "blocked"
    assert response.output_persisted is False
    assert "persist_output" in response.message.lower() or "P8-M1" in response.message


def test_response_never_includes_api_key_fields(tmp_path: Path):
    request = ProviderAdapterRequest(mode="mock", prompt="test")
    response = run_provider_adapter(request, _layout(tmp_path))
    dumped = response.model_dump()

    assert "api_key" not in dumped
    assert "secret" not in dumped or "secrets_redacted" in dumped


def test_audit_event_contains_no_raw_prompt_response_secret(tmp_path: Path):
    event = build_provider_audit_event(
        provider_mode="mock",
        operation="preview",
        status="ok",
        dry_run=True,
        live_check=False,
        network_call_made=False,
        output_persisted=False,
    )

    dumped = event.model_dump()
    assert "prompt" not in dumped or dumped.get("prompt") is None
    assert "response" not in dumped or dumped.get("response") is None
    assert "api_key" not in dumped
    assert event.prompt_recorded is False
    assert event.response_recorded is False
    assert event.secret_recorded is False


def test_audit_event_redacted_true(tmp_path: Path):
    event = build_provider_audit_event(
        provider_mode="mock",
        operation="preview",
        status="ok",
        dry_run=True,
        live_check=False,
        network_call_made=False,
        output_persisted=False,
    )
    assert event.redacted is True


def test_no_active_yaml_rubric_writes(tmp_path: Path):
    request = ProviderAdapterRequest(mode="mock", prompt="test")
    response = run_provider_adapter(request, _layout(tmp_path))

    assert response.active_yaml_modified is False
    assert response.rubric_modified is False


def test_no_reality_score_action_alignment_creation(tmp_path: Path):
    request = ProviderAdapterRequest(mode="mock", prompt="test")
    response = run_provider_adapter(request, _layout(tmp_path))

    assert response.reality_score_created is False
    assert response.action_alignment_created is False


def test_p6_false_flags_remain_false(tmp_path: Path):
    request = ProviderAdapterRequest(mode="mock", prompt="test")
    response = run_provider_adapter(request, _layout(tmp_path))

    assert response.p6_behavior_validated is False
    assert response.p6_sealed is False


def test_health_returns_real_network_calls_enabled_false():
    health = build_provider_adapter_health()
    assert health.real_network_calls_enabled is False
    assert health.secrets_redacted is True
    assert health.component == "provider-adapter"


def test_status_exposes_safety_flags(tmp_path: Path):
    status = build_provider_adapter_status(_layout(tmp_path))
    assert status.real_network_calls_enabled is False
    assert status.provider_output_persists_by_default is False
    assert status.provider_output_can_write_active_yaml is False
    assert status.provider_output_can_generate_reality_score is False
    assert status.provider_output_can_generate_action_alignment is False
    assert status.p6_behavior_validated is False
    assert status.p6_sealed is False


def test_validate_provider_request_blocks_live_check():
    request = ProviderAdapterRequest(mode="mock", prompt="test", live_check=True)
    result = validate_provider_request(request)
    assert result == "blocked"


def test_validate_provider_request_blocks_persist_output():
    request = ProviderAdapterRequest(mode="mock", prompt="test", persist_output=True)
    result = validate_provider_request(request)
    assert result == "blocked"


def test_validate_provider_request_allows_normal():
    request = ProviderAdapterRequest(mode="mock", prompt="test")
    result = validate_provider_request(request)
    assert result is None


def test_redact_provider_error_masks_details():
    exc = ValueError("secret key abc123")
    result = redact_provider_error(exc)
    assert "abc123" not in result
    assert "ValueError" in result
