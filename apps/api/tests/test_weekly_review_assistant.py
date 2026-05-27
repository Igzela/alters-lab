"""Tests for weekly review assistant service."""

from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.weekly_review_assistant import (
    WeeklyReviewAssistantHealthResponse,
    WeeklyReviewAssistantRequest,
    WeeklyReviewAssistantResponse,
    WeeklyReviewAssistantStatusResponse,
)
from alters_lab.services.weekly_review_assistant import (
    LIVE_CONFIRMATION,
    MOCK_SUGGESTION,
    build_weekly_review_assistant_health,
    build_weekly_review_assistant_status,
    run_weekly_review_assistant,
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
    return 200, b'{"choices":[{"message":{"content":"Suggestion from provider"}}]}'


def _fake_http_401(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
    return 401, b'{"error": "unauthorized"}'


def _fake_http_timeout(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
    raise TimeoutError("connection timed out")


def _req(**kwargs) -> WeeklyReviewAssistantRequest:
    defaults = {}
    defaults.update(kwargs)
    return WeeklyReviewAssistantRequest(**defaults)


# --- Health & Status ---


def test_health_returns_safety_flags():
    resp = build_weekly_review_assistant_health()
    assert resp.status == "ok"
    assert resp.component == "weekly-review-assistant"
    assert resp.output_persisted_by_default is False
    assert resp.secrets_redacted is True


def test_status_returns_p6_false_flags(tmp_path: Path):
    resp = build_weekly_review_assistant_status(_layout(tmp_path))
    assert resp.p6_behavior_validated is False
    assert resp.p6_sealed is False
    assert resp.suggestion_persistence_supported is False


# --- Disabled / Mock ---


def test_disabled_returns_skipped_no_network(tmp_path: Path):
    resp = run_weekly_review_assistant(_req(), _layout(tmp_path))
    assert resp.status == "skipped"
    assert resp.network_call_made is False
    assert resp.provider_mode == "disabled"


def test_mock_returns_deterministic_suggestion_no_network(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(ProviderConfigUpdateRequest(mode="mock"), layout)
    resp = run_weekly_review_assistant(_req(), layout)
    assert resp.status == "ok"
    assert resp.network_call_made is False
    assert resp.suggestion == MOCK_SUGGESTION
    assert resp.suggestion_label == "unverified_provider_suggestion"


# --- save_suggestion blocked ---


def test_save_suggestion_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(save_suggestion=True), layout)
    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "save_suggestion" in resp.message.lower()


# --- Dry run ---


def test_dry_run_returns_no_network(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(dry_run=True), layout)
    assert resp.status == "ok"
    assert resp.network_call_made is False
    assert resp.dry_run is True


# --- Live generation gating ---


def test_live_generation_without_confirmation_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(dry_run=False, live_generation=True), layout)
    assert resp.status == "blocked"
    assert resp.network_call_made is False
    assert "confirmation" in resp.message.lower()


def test_live_generation_wrong_confirmation_returns_blocked(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(
        _req(dry_run=False, live_generation=True, confirmation="wrong-phrase"), layout
    )
    assert resp.status == "blocked"
    assert resp.network_call_made is False


def test_live_generation_exact_confirmation_uses_provider(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_200,
    )
    assert resp.network_call_made is True
    assert resp.status == "ok"
    assert resp.suggestion == "Suggestion from provider"


# --- Provider mode override ---


def test_saved_mode_mock_request_mode_openai_blocked(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(ProviderConfigUpdateRequest(mode="mock"), layout)
    resp = run_weekly_review_assistant(
        _req(provider_mode="openai-compatible-http", dry_run=False, live_generation=True,
             confirmation=LIVE_CONFIRMATION),
        layout,
    )
    assert resp.status == "blocked"
    assert resp.network_call_made is False


def test_request_mode_disabled_always_skipped(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(
        _req(provider_mode="disabled", dry_run=False, live_generation=True,
             confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_200,
    )
    assert resp.status == "skipped"
    assert resp.network_call_made is False


def test_request_mode_mock_overrides_openai_no_network(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(
        _req(provider_mode="mock"), layout,
    )
    assert resp.status == "ok"
    assert resp.network_call_made is False
    assert resp.suggestion == MOCK_SUGGESTION


# --- Error mapping ---


def test_401_maps_auth_failed(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_401,
    )
    assert resp.status == "error"
    assert resp.network_call_made is True


def test_timeout_maps_connection_error(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION),
        layout, http_client=_fake_http_timeout,
    )
    assert resp.status == "error"
    assert resp.network_call_made is True


# --- Safety invariants ---


def test_response_never_persists_output(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(), layout)
    assert resp.suggestion_persisted is False
    assert resp.prompt_persisted is False
    assert resp.response_content_persisted is False


def test_response_never_completes_weekly_review(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(), layout)
    assert resp.weekly_review_completed is False


def test_response_never_creates_action_alignment(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(), layout)
    assert resp.action_alignment_created is False


def test_response_never_creates_reality_score(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(), layout)
    assert resp.reality_score_created is False


def test_no_active_yaml_rubric_writes(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(), layout)
    assert resp.active_yaml_modified is False
    assert resp.rubric_modified is False


def test_p6_flags_remain_false(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(), layout)
    assert resp.p6_behavior_validated is False
    assert resp.p6_sealed is False


def test_response_never_includes_api_key(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    resp = run_weekly_review_assistant(_req(), layout)
    dumped = resp.model_dump()
    assert "api_key" not in dumped
    assert "sk-" not in str(dumped)


# --- Audit event safety ---


def test_audit_event_contains_no_secret():
    from alters_lab.services.weekly_review_assistant import _build_audit_event
    event = _build_audit_event(
        provider_mode="mock", status="ok",
        dry_run=True, live_generation=False, network_call_made=False,
    )
    assert event.prompt_recorded is False
    assert event.response_recorded is False
    assert event.secret_recorded is False
    assert event.redacted is True


# --- Prompt builder does not include active YAML/rubric ---


def test_prompt_builder_excludes_active_yaml(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    captured_bodies: list[dict] = []

    def capturing_client(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
        import json
        captured_bodies.append(json.loads(body))
        return 200, b'{"choices":[{"message":{"content":"ok"}}]}'

    run_weekly_review_assistant(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION,
             raw_note_excerpt="I worked on feature X"),
        layout, http_client=capturing_client,
    )

    assert len(captured_bodies) == 1
    payload = captured_bodies[0]
    user_msg = payload["messages"][1]["content"]
    assert "active_yaml" not in user_msg.lower()
    assert "rubric" not in user_msg.lower()


# --- Requested help types ---


def test_requested_help_summarize_facts_includes_instruction(tmp_path: Path):
    layout = _configured_layout(tmp_path)
    captured_bodies: list[dict] = []

    def capturing_client(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
        import json
        captured_bodies.append(json.loads(body))
        return 200, b'{"choices":[{"message":{"content":"ok"}}]}'

    run_weekly_review_assistant(
        _req(dry_run=False, live_generation=True, confirmation=LIVE_CONFIRMATION,
             requested_help="summarize_facts"),
        layout, http_client=capturing_client,
    )

    payload = captured_bodies[0]
    user_msg = payload["messages"][1]["content"]
    assert "summarize" in user_msg.lower()


# --- Existing provider_dialogue_preview tests still pass ---


def test_provider_dialogue_preview_still_works(tmp_path: Path):
    from alters_lab.services.provider_dialogue_preview import run_provider_dialogue_preview
    from alters_lab.schemas.provider_dialogue_preview import ProviderDialoguePreviewRequest

    layout = _configured_layout(tmp_path)
    resp = run_provider_dialogue_preview(
        ProviderDialoguePreviewRequest(prompt="test"), layout
    )
    assert resp.status == "ok"
    assert resp.network_call_made is False
