"""Tests for provider-backed dialogue preview service."""

from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.provider_dialogue_preview import (
    ProviderDialoguePreviewAuditEvent,
    ProviderDialoguePreviewHealthResponse,
    ProviderDialoguePreviewRequest,
    ProviderDialoguePreviewResponse,
    ProviderDialoguePreviewStatusResponse,
)
from alters_lab.services.provider_dialogue_preview import (
    LIVE_CONFIRMATION,
    MOCK_PREVIEW,
    build_provider_dialogue_preview_audit_event,
    build_provider_dialogue_preview_health,
    build_provider_dialogue_preview_status,
    run_provider_dialogue_preview,
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


def _fake_http_200(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
    return 200, b'{"choices":[{"message":{"content":"Hello from provider"}}]}'


def _fake_http_401(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
    return 401, b'{"error": "unauthorized"}'


def _fake_http_500(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
    return 500, b'{"error": "internal"}'


def _fake_http_invalid(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
    return 200, b'not json'


def _fake_http_timeout(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
    raise TimeoutError("connection timed out")


def _req(**kwargs) -> ProviderDialoguePreviewRequest:
    defaults = {"prompt": "What is 2+2?"}
    defaults.update(kwargs)
    return ProviderDialoguePreviewRequest(**defaults)


# --- Service tests ---


def test_disabled_returns_skipped_no_network(tmp_path: Path):
    resp = run_provider_dialogue_preview(_req(), _layout(tmp_path))

    assert resp.status == "skipped"
    assert resp.network_call_made is False
    assert resp.provider_mode == "disabled"
    assert resp.output_preview is None


def test_mock_returns_unverified_preview_no_network(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(ProviderConfigUpdateRequest(mode="mock"), layout)
    resp = run_provider_dialogue_preview(_req(), layout)

    assert resp.status == "ok"
    assert resp.network_call_made is False
    assert resp.output_preview == MOCK_PREVIEW
    assert resp.output_label == "unverified_provider_preview"


def test_openai_unconfigured_returns_blocked_no_network(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    from alters_lab.services.provider_config import delete_provider_secret
    delete_provider_secret("delete-secret", "secrets_yaml_fallback", layout)

    resp = run_provider_dialogue_preview(_req(), layout)

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert resp.configured is False


def test_dry_run_returns_no_network(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(_req(dry_run=True), layout)

    assert resp.status == "ok"
    assert resp.network_call_made is False
    assert resp.dry_run is True


def test_dry_run_false_live_generation_false_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(_req(dry_run=False, live_generation=False), layout)

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "live_generation" in resp.message.lower()


def test_live_generation_without_confirmation_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(_req(dry_run=False, live_generation=True), layout)

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "confirmation" in resp.message.lower()


def test_live_generation_wrong_confirmation_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation="wrong-phrase"), layout
    )

    assert resp.status == "blocked"
    assert resp.network_call_made is False


def test_persist_output_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION, persist_output=True),
        layout,
    )

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "persist_output" in resp.message.lower()


def test_save_session_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION, save_session=True),
        layout,
    )

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "save_session" in resp.message.lower()


def test_exact_confirmation_uses_injected_client(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_200,
    )

    assert resp.network_call_made is True
    assert resp.status == "ok"
    assert resp.output_preview == "Hello from provider"


def test_chat_completions_endpoint_used(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    captured_urls: list[str] = []

    def capturing_client(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
        captured_urls.append(url)
        return 200, b'{"choices":[{"message":{"content":"ok"}}]}'

    run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=capturing_client,
    )

    assert len(captured_urls) == 1
    assert captured_urls[0].endswith("/chat/completions")


def test_only_supplied_prompt_and_system_prompt_sent(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    captured_bodies: list[dict] = []

    def capturing_client(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
        import json
        captured_bodies.append(json.loads(body))
        return 200, b'{"choices":[{"message":{"content":"ok"}}]}'

    run_provider_dialogue_preview(
        _req(
            dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION,
            prompt="What is 2+2?", system_prompt="Be concise.",
        ),
        layout, http_client=capturing_client,
    )

    assert len(captured_bodies) == 1
    payload = captured_bodies[0]
    messages = payload["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "Be concise."
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "What is 2+2?"


def test_2xx_extracts_choices_content(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_200,
    )

    assert resp.status == "ok"
    assert resp.output_preview == "Hello from provider"
    assert resp.status_code == 200


def test_401_maps_auth_failed(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_401,
    )

    assert resp.status == "error"
    assert resp.error_type == "auth_failed"
    assert resp.status_code == 401
    assert resp.network_call_made is True


def test_timeout_maps_connection_error(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_timeout,
    )

    assert resp.status == "error"
    assert resp.error_type == "connection_error"
    assert resp.network_call_made is True


def test_invalid_response_maps_invalid_response(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_invalid,
    )

    assert resp.status == "error"
    assert resp.error_type == "invalid_response"
    assert resp.network_call_made is True


def test_response_never_includes_api_key(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(_req(), layout)
    dumped = resp.model_dump()

    assert "api_key" not in dumped
    assert "sk-" not in str(dumped)


def test_audit_event_contains_no_prompt_response_secret():
    event = build_provider_dialogue_preview_audit_event(
        provider_mode="mock", status="ok",
        dry_run=True, live_generation=False, network_call_made=False,
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
    resp = run_provider_dialogue_preview(_req(), layout)

    assert resp.active_yaml_modified is False
    assert resp.rubric_modified is False
    assert resp.reality_score_created is False
    assert resp.action_alignment_created is False


def test_no_scores_created(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(_req(), layout)

    assert resp.reality_score_created is False
    assert resp.action_alignment_created is False


def test_p6_false_flags_remain_false(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(_req(), layout)

    assert resp.p6_behavior_validated is False
    assert resp.p6_sealed is False


def test_connectivity_still_works(tmp_path: Path):
    from alters_lab.services.provider_connectivity import run_provider_connectivity_check
    from alters_lab.schemas.provider_connectivity import ProviderConnectivityRequest

    resp = run_provider_connectivity_check(ProviderConnectivityRequest(), _layout(tmp_path))
    assert resp.status == "skipped"
    assert resp.network_call_made is False


def test_adapter_still_no_network(tmp_path: Path):
    from alters_lab.services.provider_adapter import run_provider_adapter
    from alters_lab.schemas.provider_adapter import ProviderAdapterRequest

    resp = run_provider_adapter(ProviderAdapterRequest(mode="mock", prompt="test"), _layout(tmp_path))
    assert resp.network_call_made is False
    assert resp.output_persisted is False


# --- Contract hardening ---


def test_response_rejects_output_persisted_true():
    with pytest.raises(Exception):
        ProviderDialoguePreviewResponse(
            status="ok", provider_mode="mock", configured=True,
            dry_run=True, live_generation=False, network_call_made=False,
            message="test", output_persisted=True,
        )


def test_response_rejects_save_session_true():
    with pytest.raises(Exception):
        ProviderDialoguePreviewResponse(
            status="ok", provider_mode="mock", configured=True,
            dry_run=True, live_generation=False, network_call_made=False,
            message="test", save_session=True,
        )


def test_response_rejects_secrets_redacted_false():
    with pytest.raises(Exception):
        ProviderDialoguePreviewResponse(
            status="ok", provider_mode="mock", configured=True,
            dry_run=True, live_generation=False, network_call_made=False,
            message="test", secrets_redacted=False,
        )


def test_response_rejects_prompt_persisted_true():
    with pytest.raises(Exception):
        ProviderDialoguePreviewResponse(
            status="ok", provider_mode="mock", configured=True,
            dry_run=True, live_generation=False, network_call_made=False,
            message="test", prompt_persisted=True,
        )


def test_health_rejects_live_generation_supported_false():
    with pytest.raises(Exception):
        ProviderDialoguePreviewHealthResponse(live_generation_supported=False)


def test_status_rejects_persistence_supported_true():
    with pytest.raises(Exception):
        ProviderDialoguePreviewStatusResponse(
            provider_mode="mock", configured=True, persistence_supported=True,
        )


# --- P8-M3-R1 regression tests ---


def test_saved_mode_mock_request_mode_openai_blocked(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(ProviderConfigUpdateRequest(mode="mock"), layout)
    resp = run_provider_dialogue_preview(
        _req(mode="openai-compatible-http", dry_run=False, live_generation=True,
             confirmation=LIVE_CONFIRMATION),
        layout,
    )

    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "saved provider mode" in resp.message.lower()


def test_saved_mode_disabled_request_mode_openai_blocked(tmp_path: Path):
    layout = _layout(tmp_path)
    # disabled is the default
    resp = run_provider_dialogue_preview(
        _req(mode="openai-compatible-http", dry_run=False, live_generation=True,
             confirmation=LIVE_CONFIRMATION),
        layout,
    )

    assert resp.status == "blocked"
    assert resp.network_call_made is False


def test_saved_mode_openai_request_mode_mock_uses_mock(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        _req(mode="mock"), layout,
    )

    assert resp.status == "ok"
    assert resp.network_call_made is False
    assert resp.output_preview == MOCK_PREVIEW


def test_secret_store_get_secret_keyring_preferred():
    from alters_lab.services.provider_config import SecretStore

    class FakeLayout:
        secrets_path = Path("/nonexistent")

    store = SecretStore(FakeLayout())  # type: ignore[arg-type]

    # keyring unavailable, storage=keyring → should fallback
    result = store.get_secret("keyring", "test-key")
    # No keyring available, so fallback is used (returns None since file doesn't exist)
    assert result is None

    # storage=secrets_yaml_fallback → always fallback
    result = store.get_secret("secrets_yaml_fallback", "test-key")
    assert result is None


def test_secret_store_get_secret_fallback_respects_storage_policy(tmp_path: Path):
    from alters_lab.services.provider_config import SecretStore, store_provider_secret
    from alters_lab.services.runtime_layout import resolve_runtime_layout

    repo = tmp_path / "repo"
    repo.mkdir()
    layout = resolve_runtime_layout(
        mode="dev", repo_root=repo,
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
    )
    store = SecretStore(layout)
    store_provider_secret("test-api-key-123", "secrets_yaml_fallback", "store-secret", layout)

    # storage=secrets_yaml_fallback → returns fallback secret
    result = store.get_secret("secrets_yaml_fallback", "alters-lab/provider-api-key")
    assert result == "test-api-key-123"

    # storage=keyring, keyring unavailable → falls back to secrets.yaml
    result = store.get_secret("keyring", "alters-lab/provider-api-key")
    assert result == "test-api-key-123"
